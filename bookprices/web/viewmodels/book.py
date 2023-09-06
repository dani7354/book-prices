from dataclasses import dataclass
from typing import Optional
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore
from bookprices.shared.model.bookprice import BookPrice


@dataclass(frozen=True)
class AuthorOption:
    text: str
    value: str
    selected: bool


@dataclass(frozen=True)
class BookListItemViewModel:
    id: int
    isbn: str
    title: str
    author: str
    url: str
    image_url: str


@dataclass(frozen=True)
class BookPriceForStoreViewModel:
    book_store_id: int
    book_store_name: str
    url: str
    price_history_url: str
    price: float
    created: str
    is_price_available: bool


@dataclass(frozen=True)
class PriceHistoryViewModel:
    book: Book
    book_store: BookStore
    book_prices: list[BookPrice]
    plot_data: str
    store_url: str
    return_url: str


@dataclass(frozen=True)
class IndexViewModel:
    book_list: list[BookListItemViewModel]
    authors: list[AuthorOption]
    search_phrase: str
    author: Optional[str]
    current_page: int
    previous_page: Optional[int]
    next_page: Optional[int]
    previous_page_url: Optional[str]
    next_page_url: Optional[str]


@dataclass(frozen=True)
class BookDetailsViewModel:
    book: Book
    book_prices: list[BookPriceForStoreViewModel]
    plot_data: str
    return_url: str
    page: Optional[int]
    search_phrase: Optional[str]
