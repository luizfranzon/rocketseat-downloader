import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class JsonSessionRepository:
    def __init__(self, path: Path):
        self._path = path

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> Optional[dict]:
        if not self._path.exists():
            return None
        logger.info("Carregando sessão salva...")
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f)
