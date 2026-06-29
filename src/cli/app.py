import logging
import os
import shutil
import sys
from pathlib import Path

from src.core.config import Settings
from src.core.exceptions import AuthenticationError
from src.core.use_cases.authenticate import AuthenticateUseCase
from src.core.use_cases.download_courses import DownloadCoursesUseCase
from src.infra.downloader.yt_dlp_downloader import YtDlpDownloader
from src.infra.http.rocketseat_client import RocketseatClient
from src.infra.report.txt_report_writer import TxtReportWriter
from src.infra.storage.json_session_repository import JsonSessionRepository

logger = logging.getLogger(__name__)


def check_dependencies() -> None:
    required = ["ffmpeg", "yt-dlp"]
    missing = [cmd for cmd in required if shutil.which(cmd) is None]
    if missing:
        print("ERRO: Dependências não encontradas. Por favor, instale:")
        for cmd in missing:
            print(f" - {cmd}")
        print("\n - FFmpeg: https://ffmpeg.org/download.html")
        print(" - yt-dlp: https://github.com/yt-dlp/yt-dlp")
        sys.exit(1)
    logger.info("Todas as dependências foram encontradas.")


def build_app():
    settings = Settings()

    session_repo = JsonSessionRepository(settings.session_path)
    http_client = RocketseatClient(settings.base_api_url)

    session_data = session_repo.load()
    if session_data:
        http_client.set_token(session_data["token"], session_data["token_type"])

    auth_use_case = AuthenticateUseCase(http_client, session_repo)
    download_use_case = DownloadCoursesUseCase(
        http=http_client,
        video_downloader=YtDlpDownloader(),
        report_writer=TxtReportWriter(Path("relatorios")),
        base_app_url=settings.base_app_url,
    )

    return session_repo, auth_use_case, download_use_case


def run() -> None:
    check_dependencies()
    logger.info("Iniciando o processo de download...")

    session_repo, auth_use_case, download_use_case = build_app()

    if not session_repo.exists():
        email = input("Seu email Rocketseat: ")
        password = input("Sua senha: ")
        try:
            auth_use_case.execute(email, password)
        except AuthenticationError as e:
            print(f"Erro de autenticação: {e}")
            sys.exit(1)

    specializations = download_use_case.get_specializations()

    os.system("cls" if os.name == "nt" else "clear")
    print("Selecione uma formação ou 0 para selecionar todas:")
    for i, spec in enumerate(specializations, 1):
        print(f"[{i}] - {spec.title}")

    choice = int(input(">> "))

    if choice == 0:
        for spec in specializations:
            modules = download_use_case.get_modules(spec.slug)
            selected = _select_modules(modules)
            download_use_case.execute(spec, selected)
    else:
        spec = specializations[choice - 1]
        modules = download_use_case.get_modules(spec.slug)
        selected = _select_modules(modules)
        download_use_case.execute(spec, selected)


def _select_modules(modules):
    print("\nEscolha os módulos que você quer baixar:")
    print("[0] - Baixar todos os módulos")
    for i, module in enumerate(modules, 1):
        print(f"[{i}] - {module.title}")

    choices = input("Digite 0 para todos ou números separados por vírgula (ex: 1, 3, 5): ")

    if choices.strip() == "0":
        return modules
    return [modules[int(c.strip()) - 1] for c in choices.split(",")]
