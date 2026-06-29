import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.base_api_url = os.getenv("BASE_API_URL", "https://skylab-api.rocketseat.com.br")
        self.base_app_url = os.getenv("BASE_APP_URL", "https://app.rocketseat.com.br")
        self.session_path = Path(os.getenv("SESSION_DIR", ".")) / ".session.json"
