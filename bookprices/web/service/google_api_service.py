import requests
from dataclasses import dataclass


@dataclass(frozen=True)
class UserInfo:
    id: str
    email: str
    picture_url: str


class GoogleApiService:
    def __init__(self, api_token: str):
        self._api_token = api_token
        self._headers = {
            "Authorization": f"Bearer {self._api_token}"
        }

    def get_user_info(self) -> UserInfo:
        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=self._headers)
        response.raise_for_status()
        json_content = response.json()
        return UserInfo(
            id=json_content["id"],
            email=json_content["email"],
            picture_url=json_content["picture"])
