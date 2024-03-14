import os
from typing import ClassVar
from flask import session


class CSRFService:
    _token_size: ClassVar[int] = 32
    _token_session_key: ClassVar[str] = "csrf_token"

    def generate_token(self) -> str:
        session[self._token_session_key] = os.urandom(self._token_size).hex()
        return session[self._token_session_key]

    def is_token_valid(self, token: str) -> bool:
        return session.get(self._token_session_key) == token


def get_csrf_token() -> dict[str, str]:
    csrf_service = CSRFService()
    csrf_token = csrf_service.generate_token()

    return {"csrf_token": csrf_token}
