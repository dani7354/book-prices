from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    id: int
    isbn: str
    title: str
    author: str
    format: str
    image_url: Optional[str] = None
    created: str | datetime | None = None
