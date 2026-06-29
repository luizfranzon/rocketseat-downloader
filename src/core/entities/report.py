from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DownloadEntry:
    module: str
    lesson: str
    timestamp: datetime


@dataclass
class FailureEntry:
    module: str
    lesson: str
    error: str
    timestamp: datetime


@dataclass
class Report:
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    successful: list[DownloadEntry] = field(default_factory=list)
    failed: list[FailureEntry] = field(default_factory=list)

    def start(self):
        self.start_time = datetime.now()

    def finish(self):
        self.end_time = datetime.now()

    def add_success(self, module: str, lesson: str):
        self.successful.append(DownloadEntry(module, lesson, datetime.now()))

    def add_failure(self, module: str, lesson: str, error: str):
        self.failed.append(FailureEntry(module, lesson, error, datetime.now()))
