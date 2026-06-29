import logging
import subprocess
from pathlib import Path

from src.core.exceptions import DownloadError

logger = logging.getLogger(__name__)

_CDN_DOMAIN = "vz-dc851587-83d.b-cdn.net"
_CDN_REFERER = "https://iframe.mediadelivery.net/"
_CDN_ORIGIN = "https://iframe.mediadelivery.net"


class YtDlpDownloader:
    def download(self, video_id: str, save_path: Path) -> None:
        if save_path.exists():
            logger.info(f"Arquivo já existe: {save_path.name}. Pulando.")
            return

        playlist_url = f"https://{_CDN_DOMAIN}/{video_id}/playlist.m3u8"
        logger.info(f"Baixando com yt-dlp: {save_path.name}")

        try:
            subprocess.run(
                [
                    "yt-dlp", playlist_url,
                    "--merge-output-format", "mp4",
                    "--concurrent-fragments", "10",
                    "--add-header", f"Referer: {_CDN_REFERER}",
                    "--add-header", f"Origin: {_CDN_ORIGIN}",
                    "-o", str(save_path),
                ],
                check=True,
            )
            logger.info("Download concluído com sucesso!")
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"yt-dlp falhou para {video_id}: {e}") from e
