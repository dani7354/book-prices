import logging
from typing import ClassVar, Callable

import requests
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
        try:
            response = requests.get(
                url=self.format_url(endpoint),
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_get, endpoint)
            raise

    def post(self, endpoint: str, json: dict) -> dict:
        return self._send_post(endpoint, json)

    def _send_post(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        try:
            response = requests.post(
                url=self.format_url(endpoint),
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_post, endpoint, json)
            raise

    def put(self, endpoint: str, json: dict) -> dict:
        return self._send_put(endpoint, json)

    def _send_put(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        try:
            response = requests.put(
                url=self.format_url(endpoint),
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_put, endpoint, json)
            raise

    def patch(self, endpoint: str, json: dict) -> dict:
        return self._send_patch(endpoint, json)

    def _send_patch(self, endpoint: str, json: dict, is_retry: bool = False) -> dict:
        try:
            response = requests.patch(
                url=self.format_url(endpoint),
                data=json,
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == codes.unauthorized and not is_retry:
                return self._refresh_key_and_retry(self._send_patch, endpoint, json)
            raise

    def delete(self, endpoint: str) -> dict:
        return self._send_delete(endpoint)

    def _send_delete(self, endpoint: str, is_retry: bool = False) -> dict:
        try:
            response = requests.delete(
                url=self.format_url(endpoint),
                headers=self.get_request_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
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
        response = requests.post(
            url=f"{self._base_url}{Endpoint.LOGIN.value}",
            json={"username": self._api_username, "password": self._api_password},
            headers=self.get_request_headers())
        response.raise_for_status()
        api_key = response.content.decode(self.response_encoding).strip("\"")
        self._add_or_update_api_key_in_db(api_key)

    def _set_api_key(self) -> None:
        if not (api_key := self._api_key_db.get_api_key(self.api_name)):
            self._refresh_api_key()
            api_key = self._api_key_db.get_api_key(self.api_name)
        self._api_key = api_key.api_key

    def _add_or_update_api_key_in_db(self, api_key: str) -> None:
        if old_api_key := self._api_key_db.get_api_key(self.api_name):
            old_api_key.api_key = api_key
            self._api_key_db.update_api_key(old_api_key)
        else:
            self._api_key_db.add_api_key(ApiKey(
                id=None,
                api_name=self.api_name,
                api_user=self._api_username,
                api_key=api_key))
