import dataclasses
from enum import StrEnum
from typing import ClassVar
from random import getrandbits

import requests
from logging import getLogger


class RequestFailedError(Exception):
    pass


class HttpHeader(StrEnum):
    USER_AGENT = "User-Agent"
    ACCEPT = "Accept"


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    redirected: bool
    status_code: int
    url: str
    text: str


class HttpClient:
    """ Wrapper for requests library """
    _default_timeout_seconds: ClassVar[int] = 5

    def __init__(self, headers: dict[str, str] | None = None, timeout_seconds: int | None = None) -> None:
        self._logger = getLogger(self.__class__.__name__)
        self._session = requests.Session()
        self._timeout_seconds = timeout_seconds if timeout_seconds is not None else self._default_timeout_seconds

        merged_request_headers = self._get_default_headers(headers)
        merged_request_headers.update(headers or {})
        self._session.headers.update(merged_request_headers)

    def get(self, url: str) -> HttpResponse:
        try:
            response = self._session.get(url, timeout=self._timeout_seconds)
            response.raise_for_status()
            redirected = response.history != []

            return HttpResponse(
                redirected=redirected,
                status_code=response.status_code,
                text=response.text,
                url=response.url
            )
        except requests.RequestException as e:
            self._logger.error(f"HTTP GET request to {url} failed: {e}")
            raise RequestFailedError from e

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            self._session.close()
        except Exception as e:
            self._logger.error(f"Failed to close HTTP session: {e}")

    @classmethod
    def _get_default_headers(cls, custom_headers: dict[str, str] | None) -> dict[str, str]:
        merged_headers = {}
        if not custom_headers or HttpHeader.USER_AGENT not in custom_headers:
            merged_headers[HttpHeader.USER_AGENT] = cls._get_ua_header_value_random_versions()
        if not custom_headers or HttpHeader.ACCEPT not in custom_headers:
            merged_headers[HttpHeader.ACCEPT] = (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7")

        return merged_headers

    @staticmethod
    def _get_ua_header_value_random_versions() -> str:
        ff_version = getrandbits(3) + 140

        return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ff_version}.0.0.0 Safari/537.36"
