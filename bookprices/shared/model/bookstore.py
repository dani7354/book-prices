import urllib.parse
from bookprices.shared.model.book import Book


class BookStore:
    def __init__(self,
                 id: int,
                 name: str,
                 url: str,
                 search_url: str | None,
                 search_result_css_selector: str | None,
                 price_css_selector: str | None,
                 image_css_selector: str | None,
                 price_format: str | None):
        self.id = id
        self.name = name
        self.url = url
        self.search_url = search_url
        self.search_result_css_selector = search_result_css_selector
        self.price_css_selector = price_css_selector
        self.image_css_selector = image_css_selector
        self.price_format = price_format


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
