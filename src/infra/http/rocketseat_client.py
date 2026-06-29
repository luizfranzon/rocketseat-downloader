import logging
from pathlib import Path

import requests

from src.core.exceptions import ApiError

logger = logging.getLogger(__name__)


class RocketseatClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://app.rocketseat.com.br",
        })

    def set_token(self, token: str, token_type: str) -> None:
        self._session.headers["Authorization"] = f"{token_type} {token}"
        self._session.cookies.update({"skylab_next_access_token_v3": token})

    def get(self, path: str, params: dict | None = None) -> dict:
        try:
            response = self._session.get(f"{self._base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise ApiError(f"HTTP error on GET {path}: {e}") from e

    def post(self, path: str, data: dict) -> dict:
        try:
            response = self._session.post(f"{self._base_url}{path}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise ApiError(f"HTTP error on POST {path}: {e}") from e

    def get_text(self, url: str) -> str:
        try:
            response = self._session.get(url)
            response.raise_for_status()
            return response.text
        except requests.HTTPError as e:
            raise ApiError(f"HTTP error fetching HTML {url}: {e}") from e

    def download_file(self, url: str, dest: Path) -> None:
        try:
            response = requests.get(url)
            response.raise_for_status()
            dest.write_bytes(response.content)
        except Exception as e:
            raise ApiError(f"Erro ao baixar arquivo de {url}: {e}") from e
