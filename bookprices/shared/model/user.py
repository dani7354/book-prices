from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class UserAccessLevel(Enum):
    MEMBER = 0x1
    JOB_MANAGER = 0xa
    ADMIN = 0xff

    @staticmethod
    def from_string(str_value: str) -> Optional["UserAccessLevel"]:
        return next((al for al in UserAccessLevel if al.name.upper() == str_value.upper()), None)


@dataclass(frozen=True)
class User:
    id: str
    booklist_id: int | None
    email: str
    firstname: str
    lastname: str | None
    is_active: bool
    google_api_token: str
    image_url: Optional[str]
    access_level: UserAccessLevel
    created: datetime
    updated: datetime
