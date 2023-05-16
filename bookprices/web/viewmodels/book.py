from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore
from bookprices.shared.model.bookprice import BookPrice


class BookListItemViewModel:
    def __init__(self, id: int, isbn: str, title: str, author: str, image_url: str):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.image_url = image_url


class BookPriceForStoreViewModel:
    def __init__(self,
                 book_store_id: int,
                 book_store_name: str,
                 url: str,
                 price: float,
                 created: str,
                 is_price_available: bool):

        self.book_store_id = book_store_id
        self.book_store_name = book_store_name
        self.url = url
        self.price = price
        self.created = created
        self.is_price_available = is_price_available


class PriceHistoryViewModel:
    def __init__(self,
                 book: Book,
                 book_store: BookStore,
                 book_prices: list[BookPrice],
                 url: str):

        self.book = book
        self.book_store = book_store
        self.book_prices = book_prices
        self.url = url


class IndexViewModel:
    def __init__(self,
                 book_list: list[BookListItemViewModel],
                 search_phrase: str,
                 current_page: int,
                 previous_page: int | None,
                 next_page: int | None):
        self.book_list = book_list
        self.search_phrase = search_phrase
        self.current_page = current_page
        self.previous_page = previous_page
        self.next_page = next_page


class BookDetailsViewModel:
    def __init__(self,
                 book: Book,
                 book_prices: list[BookPriceForStoreViewModel],
                 index_url: str):
        self.book = book
        self.book_prices = book_prices
        self.index_url = index_url
