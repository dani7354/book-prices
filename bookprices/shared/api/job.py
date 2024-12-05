import requests

from bookprices.shared.db.api import ApiKeyDb


class JobApiClient:
    def __init__(self, base_url: str, api_key_db: ApiKeyDb) -> None:
        self._base_url = base_url
        self._api_key_db = api_key_db
