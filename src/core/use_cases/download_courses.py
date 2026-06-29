import logging
import re
from pathlib import Path

from src.core.entities.lesson import Download, Group, Lesson, Module, Specialization
from src.core.entities.report import Report
from src.core.ports.http_client import HttpClientPort
from src.core.ports.report_writer import ReportWriterPort
from src.core.ports.video_downloader import VideoDownloaderPort

logger = logging.getLogger(__name__)

_SANITIZE_RE = re.compile(r'[@#$%&*/:^{}<>?"|\\]')


def _sanitize(text: str) -> str:
    return _SANITIZE_RE.sub("", text).strip()


class DownloadCoursesUseCase:
    def __init__(
        self,
        http: HttpClientPort,
        video_downloader: VideoDownloaderPort,
        report_writer: ReportWriterPort,
        base_app_url: str,
    ):
        self._http = http
        self._video_downloader = video_downloader
        self._report_writer = report_writer
        self._base_app_url = base_app_url

    def get_specializations(self) -> list[Specialization]:
        params = {
            "types[0]": "SPECIALIZATION",
            "types[1]": "COURSE",
            "types[2]": "EXTRA",
            "limit": "60",
            "offset": "0",
            "page": "1",
            "sort_by": "relevance",
        }
        data = self._http.get("/catalog/list", params=params)
        return [Specialization(title=item["title"], slug=item["slug"]) for item in data["items"]]

    def get_modules(self, specialization_slug: str) -> list[Module]:
        logger.info(f"Buscando módulos para: {specialization_slug}")
        data = self._http.get(f"/v2/journeys/{specialization_slug}/progress/temp")
        nodes = data.get("nodes", [])

        journey_url = f"{self._base_app_url}/journey/{specialization_slug}/contents"
        html = self._http.get_text(journey_url)
        slugs_map = self._extract_slugs(html)

        modules = []
        for node in nodes:
            if node.get("type") in ("challenge", "micro-certificate"):
                continue

            title = node.get("title", "").strip()
            cluster_slug = node.get("slug")

            if node.get("type") in ("cluster", "group") and not cluster_slug:
                cluster_slug = slugs_map.get(title)
                if cluster_slug:
                    logger.info(f"Slug recuperado via HTML para '{title}': {cluster_slug}")

            modules.append(Module(
                title=title,
                type=node.get("type", ""),
                slug=node.get("slug"),
                cluster_slug=cluster_slug,
            ))

        logger.info(f"Encontrados {len(modules)} módulos.")
        return modules

    def _extract_slugs(self, html: str) -> dict[str, str]:
        pattern = re.compile(r'\\"title\\":\\"(?P<title>[^\\"]+)\\".*?\\"slug\\":\\"(?P<slug>[^\\"]+)\\"')
        result: dict[str, str] = {}
        for title, slug in pattern.findall(html):
            clean = title.strip()
            if clean not in result:
                result[clean] = slug
        logger.info(f"Mapeamento de slugs via HTML: {len(result)} itens encontrados.")
        return result

    def _get_groups(self, cluster_slug: str) -> list[Group]:
        try:
            data = self._http.get(f"/journey-nodes/{cluster_slug}")
        except Exception as e:
            logger.error(f"Erro ao buscar cluster {cluster_slug}: {e}")
            return []

        groups = []
        if data.get("cluster"):
            for group_data in data["cluster"].get("groups", []):
                group = self._parse_group(group_data)
                if group:
                    groups.append(group)
        elif data.get("group"):
            group = self._parse_group(data["group"])
            if group:
                groups.append(group)

        return groups

    def _parse_group(self, group_data: dict) -> Group | None:
        group_title = group_data.get("title", "Sem Grupo")
        lessons = []

        for lesson_raw in group_data.get("lessons", []):
            if not lesson_raw.get("last"):
                continue

            ld = lesson_raw["last"]
            author = ""
            if isinstance(ld.get("author"), dict):
                author = ld["author"].get("name", "")

            resource = ld.get("resource", "")
            if resource and "/" in resource:
                resource = resource.split("/")[-1]

            downloads = [
                Download(title=d.get("title", "arquivo"), file_url=d["file_url"])
                for d in ld.get("downloads", [])
                if d.get("file_url")
            ]

            lessons.append(Lesson(
                title=ld.get("title", "Sem título"),
                group_title=group_title,
                resource=resource or None,
                description=ld.get("description"),
                duration=ld.get("duration"),
                author=author or None,
                downloads=downloads,
            ))

        return Group(title=group_title, lessons=lessons) if lessons else None

    def execute(self, specialization: Specialization, modules: list[Module]) -> None:
        report = Report()
        report.start()
        logger.info(f"Início do download: {report.start_time.strftime('%d/%m/%Y %H:%M:%S')}")

        module_groups = [
            (m, self._get_groups(m.cluster_slug))
            for m in modules
            if m.cluster_slug
        ]

        total = sum(len(g.lessons) for _, groups in module_groups for g in groups)
        logger.info(f"Total de aulas: {total}")
        lesson_counter = 0

        try:
            for module_index, (module, groups) in enumerate(module_groups, 1):
                base_path = Path("Cursos") / _sanitize(specialization.title)
                save_path = base_path / f"{module_index:02d}. {_sanitize(module.title)}"
                save_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"\nBaixando módulo: {module.title}")

                for group_index, group in enumerate(groups, 1):
                    for lesson_index, lesson in enumerate(group.lessons, 1):
                        lesson_counter += 1
                        self._download_lesson(
                            lesson, save_path, group_index, lesson_index,
                            lesson_counter, total, report,
                        )
        finally:
            report.finish()
            self._report_writer.write(report)

    def _download_lesson(
        self,
        lesson: Lesson,
        save_path: Path,
        group_index: int,
        lesson_index: int,
        counter: int,
        total: int,
        report: Report,
    ) -> None:
        logger.info(f"\033[32m[{counter}/{total}]\033[0m Baixando {group_index}.{lesson_index}: {lesson.title}")

        try:
            group_folder = save_path / f"{group_index:02d}. {_sanitize(lesson.group_title)}"
            group_folder.mkdir(exist_ok=True)

            base_name = f"{lesson_index:02d}. {_sanitize(lesson.title)}"
            video_path = group_folder / f"{base_name}.mp4"

            if lesson.resource and video_path.exists():
                logger.info(f"Aula '{lesson.title}' já baixada. Pulando.")
                return

            self._write_metadata(lesson, group_folder / f"{base_name}.txt")

            if lesson.resource:
                self._video_downloader.download(lesson.resource, video_path)

            if lesson.downloads:
                materials_dir = group_folder / f"{base_name}_arquivos"
                materials_dir.mkdir(exist_ok=True)
                for dl in lesson.downloads:
                    ext = Path(dl.file_url).suffix
                    dest = materials_dir / f"{_sanitize(dl.title)}{ext}"
                    logger.info(f"Baixando material: {dl.title}")
                    self._http.download_file(dl.file_url, dest)

            report.add_success(lesson.group_title, lesson.title)
        except Exception as e:
            report.add_failure(lesson.group_title, lesson.title, str(e))
            logger.error(f"Erro ao baixar aula {lesson.title}: {e}")

    def _write_metadata(self, lesson: Lesson, path: Path) -> None:
        lines = [f"Grupo: {lesson.group_title}", f"Aula: {lesson.title}", ""]

        if lesson.description:
            lines += [f"Descrição:\n{lesson.description}", ""]

        if lesson.duration is not None:
            lines.append(f"Duração: {lesson.duration // 60}min {lesson.duration % 60}s")

        if lesson.author:
            lines.append(f"Autor: {lesson.author}")

        path.write_text("\n".join(lines), encoding="utf-8")
