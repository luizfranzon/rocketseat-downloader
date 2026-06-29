from pathlib import Path
from typing import Protocol


class VideoDownloaderPort(Protocol):
    def download(self, video_id: str, save_path: Path) -> None: ...
