from dataclasses import dataclass
from bookprices.shared.model.bookstore import BookStore


@dataclass(frozen=True)
class AboutViewModel:
    bookstores: list[BookStore]
