import dataclasses
from collections import deque
from enum import StrEnum
from threading import Lock
from typing import ClassVar
from random import getrandbits
from time import monotonic, sleep

import requests
from logging import getLogger


class RequestFailedError(Exception):
    pass


class HttpHeaderName(StrEnum):
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

    def close_session(self) -> None:
        self._session.close()

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
        if not custom_headers or HttpHeaderName.USER_AGENT not in custom_headers:
            merged_headers[HttpHeaderName.USER_AGENT] = cls._get_ua_header_value_random_versions()
        if not custom_headers or HttpHeaderName.ACCEPT not in custom_headers:
            merged_headers[HttpHeaderName.ACCEPT] = (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7")

        return merged_headers

    @staticmethod
    def _get_ua_header_value_random_versions() -> str:
        ff_version = getrandbits(3) + 140

        return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ff_version}.0.0.0 Safari/537.36"


class RateLimiter:
    """ Rate limiter for use with HTTP requests. """
    _default_sleep_time: ClassVar[float] = 0.05

    def __init__(self, request_count: int, seconds: int) -> None:
        self._request_count = request_count
        self._seconds = seconds
        self._request_timestamps: deque[float] = deque()
        self._lock = Lock()
        self._logger = getLogger(self.__class__.__name__)

    def wait_if_needed(self) -> None:
        while True:
            with self._lock:
                now = monotonic()
                self._remove_expired_timestamps(now)

                if len(self._request_timestamps) < self._request_count:
                    self._request_timestamps.append(now)
                    return

                earliest = self._request_timestamps[0]
                wait_time = self._seconds - (now - earliest)

            sleeping_time = max(wait_time, self._default_sleep_time)
            self._logger.debug(f"Rate limit hit! Sleeping for {sleeping_time} seconds...")
            sleep(sleeping_time)

    def _remove_expired_timestamps(self, now: float) -> None:
        while self._request_timestamps and (now - self._request_timestamps[0]) >= self._seconds:
            self._request_timestamps.popleft()
