import logging

from src.core.exceptions import AuthenticationError
from src.core.ports.http_client import HttpClientPort
from src.core.ports.session_storage import SessionStoragePort

logger = logging.getLogger(__name__)


class AuthenticateUseCase:
    def __init__(self, http: HttpClientPort, storage: SessionStoragePort):
        self._http = http
        self._storage = storage

    def execute(self, email: str, password: str) -> str:
        logger.info("Realizando login...")
        try:
            data = self._http.post("/sessions", {"email": email, "password": password})
            token = data["token"]
            refresh_token = data["refreshToken"]
            token_type = data["type"].capitalize()

            self._http.set_token(token, token_type)
            self._storage.save({
                "token": token,
                "refresh_token": refresh_token,
                "token_type": token_type,
            })

            account = self._http.get("/account")
            name = account.get("name", "")
            logger.info(f"Bem-vindo, {name}!")
            return name
        except Exception as e:
            raise AuthenticationError(f"Falha no login: {e}") from e
