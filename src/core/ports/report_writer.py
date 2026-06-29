from typing import Protocol

from src.core.entities.report import Report


class ReportWriterPort(Protocol):
    def write(self, report: Report) -> None: ...
