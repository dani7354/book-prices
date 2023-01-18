import urllib.parse


class Book:
    def __init__(self, id, title, author):
        self.id = id
        self.title = title
        self.author = author


class BookStore:
    def __init__(self, id, name, url, price_css_selector, price_format):
        self.id = id
        self.name = name
        self.url = url
        self.price_css_selector = price_css_selector
        self.price_format = price_format


class BookInBookStore:
    def __init__(self, book, book_store, url):
        self.book = book
        self.book_store = book_store
        self.url = url

    def get_full_url(self):
        return urllib.parse.urljoin(self.book_store.url, self.url)


class BookPrice:
    def __init__(self, id, book, book_store, price, created):
        self.id = id
        self.book = book
        self.book_store = book_store
        self.price = price
        self.created = created
