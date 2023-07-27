import urllib.parse
from dataclasses import dataclass
from typing import Optional
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
    price_format: Optional[str]


class BookInBookStore:
    def __init__(self, book: Book, book_store: BookStore, url: str):
        self.book = book
        self.book_store = book_store
        self.url = url

    def get_full_url(self) -> str:
        return urllib.parse.urljoin(self.book_store.url, self.url)


class BookStoreBookPrice:
    def __init__(self,
                 id: int,
                 book_store_id: int,
                 book_store_name: str,
                 url: str,
                 price: float,
                 created: str):
        self.id = id
        self.book_store_id = book_store_id
        self.book_store_name = book_store_name
        self.url = url
        self.price = price
        self.created = created


class BookStoreSitemap:
    def __init__(self, id: int, url: str, book_store: BookStore):
        self.id = id
        self.url = url
        self.book_store = book_store
