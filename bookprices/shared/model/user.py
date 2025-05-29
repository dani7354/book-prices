from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class UserAccessLevel(Enum):
    ADMIN = 0xff
    MEMBER = 0x1


@dataclass(frozen=True)
class User:
    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    google_api_token: str
    image_url: Optional[str]
    access_level: UserAccessLevel
    created: datetime
    updated: datetime
