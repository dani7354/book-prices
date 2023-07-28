from dataclasses import dataclass
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore


@dataclass(frozen=True)
class BookPrice:
    id: int
    book: Book
    book_store: BookStore
    price: float
    created: str
