from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore


class BookPrice:
    def __init__(self, id: int, book: Book, book_store: BookStore, price: float, created: str):
        self.id = id
        self.book = book
        self.book_store = book_store
        self.price = price
        self.created = created