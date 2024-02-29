from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    google_api_token: str
    created: datetime
    updated: datetime

    def get_id(self) -> str:
        return self.id
