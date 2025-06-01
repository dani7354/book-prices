from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class UserAccessLevel(Enum):
    MEMBER = 0x1
    JOB_MANAGER = 0xa
    ADMIN = 0xff



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
