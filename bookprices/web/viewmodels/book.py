class IndexViewModel:
    def __init__(self, book_list: list, search_phrase: str):
        self.book_list = book_list
        self.search_phrase = search_phrase


class BookListItemViewModel:
    def __init__(self, id: int, isbn: str, title: str, author: str, image_url: str):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.image_url = image_url


class BookDetailsViewModel:
    def __init__(self, book, book_prices):
        self.book = book
        self.book_prices = book_prices


class BookPriceForStoreViewModel:
    def __init__(self, book_store_id, book_store_name, url, price, created, is_price_available):
        self.book_store_id = book_store_id
        self.book_store_name = book_store_name
        self.url = url
        self.price = price
        self.created = created
        self.is_price_available = is_price_available


class PriceHistoryViewModel:
    def __init__(self, book, book_store, book_prices, url):
        self.book = book
        self.book_store = book_store
        self.book_prices = book_prices
        self.url = url
