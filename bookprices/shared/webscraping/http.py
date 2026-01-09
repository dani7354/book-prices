import dataclasses
from typing import ClassVar

import requests
from logging import getLogger


class RequestFailedError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    redirected: bool
    status_code: int
    url: str
    text: str


class HttpClient:
    """ Wrapper for requests library """
    _default_timeout_seconds: ClassVar[int] = 5
    _default_request_headers: ClassVar[dict[str, str]] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko)"
    }

    def __init__(self, headers: dict[str, str] | None = None, timeout_seconds: int | None = None) -> None:
        self._logger = getLogger(self.__class__.__name__)
        self._session = requests.Session()
        self._timeout_seconds = timeout_seconds if timeout_seconds is not None else self._default_timeout_seconds

        merged_request_headers = self._default_request_headers.copy()
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
