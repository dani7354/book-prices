class BookListItemViewModel:
    def __init__(self, id, title, author):
        self.id = id
        self.title = title
        self.author = author


class BookDetailsViewModel:
    def __init__(self, book, book_prices):
        self.book = book
        self.book_prices = book_prices


class BookPriceForStoreViewModel:
    def __init__(self, book_store_id, book_store_name, url, price, created):
        self.book_store_id = book_store_id
        self.book_store_name = book_store_name
        self.url = url
        self.price = price
        self.created = created


class PriceHistoryViewModel:
    def __init__(self, book, book_store, book_prices, url):
        self.book = book
        self.book_store = book_store
        self.book_prices = book_prices
        self.url = url
