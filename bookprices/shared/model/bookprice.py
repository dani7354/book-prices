from dataclasses import dataclass
from datetime import datetime
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore


@dataclass(frozen=True)
class BookPrice:
    id: int
    book: Book
    book_store: BookStore
    price: float
    created: datetime


@dataclass(frozen=True)
class BookPriceIds:
    id: int
    book_id: int
    bookstore_id: int
