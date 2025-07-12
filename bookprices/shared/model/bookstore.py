from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin
from bookprices.shared.model.book import Book


@dataclass(frozen=True)
class BookStore:
    id: int
    name: str
    url: str
    search_url: Optional[str]
    search_result_css_selector: Optional[str]
    price_css_selector: Optional[str]
    image_css_selector: Optional[str]
    isbn_css_selector: Optional[str]
    price_format: Optional[str]
    color_hex: Optional[str]
    has_dynamically_loaded_content: bool


@dataclass(frozen=True)
class BookInBookStore:
    book: Book
    book_store: BookStore
    url: str

    def get_full_url(self) -> str:
        return urljoin(self.book_store.url, self.url)


@dataclass(frozen=True)
class BookStoreBookPrice:
    id: int
    book_store_id: int
    book_store_name: str
    url: str
    price: float
    created: str


@dataclass(frozen=True)
class BookStoreSitemap:
    id: int
    url: str
    book_store: BookStore
