from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    google_api_token: str
    image_url: Optional[str]
    created: datetime
    updated: datetime
