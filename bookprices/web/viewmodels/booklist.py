from dataclasses import dataclass


@dataclass(frozen=True)
class BookListItemViewModel:
    id: int
    name: str
    created: str
    updated: str
    url: str


@dataclass(frozen=True)
class BookListIndexViewModel:
    create_url: str
    booklists: list[BookListItemViewModel]


@dataclass(frozen=True)
class BookListDetailsViewModel:
    books: list
    return_url: str
    name: str
    created: str
    updated: str
