from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BookList:
    id: int
    user_id: str
    name: str
    created: datetime
    updated: datetime


@dataclass(frozen=True)
class BookListBook:
    booklist_id: int
    book_id: int
    created: datetime
