from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: int
    isbn: str
    title: str
    author: str
    format: str
    image_url: Optional[str]
    created: Optional[str] = None
