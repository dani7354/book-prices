import logging
import requests
from typing import ClassVar, Callable

from requests.exceptions import HTTPError
from requests.status_codes import codes
from enum import Enum
from bookprices.shared.db.api import ApiKeyDb
from bookprices.shared.model.api import ApiKey


logger = logging.getLogger(__name__)


class Endpoint(Enum):
    LOGIN = "/api/auth/login"
    JOBS = "/api/jobs"
    JOB = "/api/jobs/{id}"
    JOB_RUNS = "/api/jobruns"
    JOB_RUN = "/api/jobruns/{id}"

    @classmethod
    def get_job_url(cls, job_id: str) -> str:
        return cls.JOB.value.format(id=job_id)

    @classmethod
    def get_job_run_url(cls, job_run_id: str) -> str:
        return cls.JOB_RUN.value.format(id=job_run_id)


class JobApiClient:
    api_name: ClassVar[str] = "JobApi"
    response_encoding: ClassVar[str] = "utf-8"

    def __init__(self, base_url: str, api_username: str, api_password: str, api_key_db: ApiKeyDb) -> None:
        self._base_url = base_url
        self._api_username = api_username
        self._api_password = api_password
        self._api_key_db = api_key_db
        self._api_key = None
        self._set_api_key()

    def get(self, endpoint: str) -> dict:
        return self._send_get(endpoint)

    def _send_get(self, endpoint: str, is_retry: bool = False) -> dict:
        url = self.format_url(endpoint)
        try:
            response = requests.get(
                url=url,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error("Failed to send GET request to %s. Error: %s", url, e)
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_get, endpoint)
            raise

    def post(self, endpoint: str, json: dict) -> dict:
        return self._send_post(endpoint, json)

    def _send_post(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        url = self.format_url(endpoint)
        try:
            response = requests.post(
                url=url,
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error("Failed to send POST request to %s. Error: %s", url, e)
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_post, endpoint, json)
            raise

    def put(self, endpoint: str, json: dict) -> dict:
        return self._send_put(endpoint, json)

    def _send_put(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        url = self.format_url(endpoint)
        try:
            response = requests.put(
                url=url,
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error("Failed to send PUT request to %s. Error: %s", url, e)
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_put, endpoint, json)
            raise

    def patch(self, endpoint: str, json: dict) -> dict:
        return self._send_patch(endpoint, json)

    def _send_patch(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        url = self.format_url(endpoint)
        try:
            response = requests.patch(
                url=url,
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error("Failed to send PATCH request to %s. Error: %s", url, e)
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_patch, endpoint, json)
            raise

    def delete(self, endpoint: str) -> dict:
        return self._send_delete(endpoint)

    def _send_delete(self, endpoint: str, is_retry: bool = False) -> dict:
        url = self.format_url(endpoint)
        try:
            response = requests.delete(
                url=url,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error("Failed to send DELETE request to %s. Error: %s", url, e)
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_delete, endpoint)
            raise

    def _refresh_key_and_retry(
            self,
            request_func: Callable[[str, dict, bool], dict] | Callable[[str, bool], dict],
            endpoint: str,
            json: dict | None = None) -> dict:
        self._refresh_api_key()
        self._set_api_key()
        return request_func(endpoint, json, True) if json else request_func(endpoint, True)

    def get_request_headers(self) -> dict:
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self._api_key:
            request_headers["Authorization"] = f"Bearer {self._api_key}"

        return request_headers

    def format_url(self, endpoint: str) -> str:
        return f"{self._base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _refresh_api_key(self) -> None:
        logger.info("Refreshing Job API key for user %s...", self._api_username)
        response = requests.post(
            url=f"{self._base_url}{Endpoint.LOGIN.value}",
            json={"username": self._api_username, "password": self._api_password},
            headers=self.get_request_headers())
        response.raise_for_status()
        api_key = response.content.decode(self.response_encoding).strip("\"")  # TODO: fix response format in API instead
        self._add_or_update_api_key_in_db(api_key)

    def _set_api_key(self) -> None:
        if not (api_key := self._api_key_db.get_api_key(self.api_name)):
            self._refresh_api_key()
            api_key = self._api_key_db.get_api_key(self.api_name)
        self._api_key = api_key.api_key

    def _add_or_update_api_key_in_db(self, api_key: str) -> None:
        if old_api_key := self._api_key_db.get_api_key(self.api_name):
            logger.info("Updating Job API key for user %s...", self._api_username)
            old_api_key.api_key = api_key
            self._api_key_db.update_api_key(old_api_key)
        else:
            logger.info("Adding Job API key for user %s to database...", self._api_username)
            self._api_key_db.add_api_key(ApiKey(
                id=None,
                api_name=self.api_name,
                api_user=self._api_username,
                api_key=api_key))
