import logging
from pathlib import Path

from src.core.entities.report import Report

logger = logging.getLogger(__name__)


class TxtReportWriter:
    def __init__(self, output_dir: Path):
        self._output_dir = output_dir

    def write(self, report: Report) -> None:
        if not report.start_time or not report.end_time:
            return

        duration = report.end_time - report.start_time
        total = len(report.successful) + len(report.failed)

        lines = [
            "=== RELATÓRIO DE DOWNLOAD ===",
            f"Data: {report.end_time.strftime('%d/%m/%Y %H:%M:%S')}",
            f"Duração total: {duration}",
            f"Total de aulas: {total}",
            f"Aulas baixadas com sucesso: {len(report.successful)}",
            f"Aulas com erro: {len(report.failed)}",
            "\n=== AULAS BAIXADAS COM SUCESSO ===",
        ]

        for entry in report.successful:
            lines += [
                f"- Módulo: {entry.module}",
                f"  Aula: {entry.lesson}",
                f"  Horário: {entry.timestamp.strftime('%H:%M:%S')}",
            ]

        if report.failed:
            lines.append("\n=== AULAS COM ERRO ===")
            for entry in report.failed:
                lines += [
                    f"- Módulo: {entry.module}",
                    f"  Aula: {entry.lesson}",
                    f"  Erro: {entry.error}",
                    f"  Horário: {entry.timestamp.strftime('%H:%M:%S')}",
                ]

        text = "\n".join(lines)
        self._output_dir.mkdir(exist_ok=True)
        path = self._output_dir / f"relatorio_{report.end_time.strftime('%Y%m%d_%H%M%S')}.txt"
        path.write_text(text, encoding="utf-8")

        logger.info("\n" + "=" * 50)
        logger.info(text)
        logger.info("=" * 50)
        logger.info(f"Relatório salvo em: {path}")
