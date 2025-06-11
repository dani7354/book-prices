from flask_caching import Cache

from bookprices.shared.cache.key_generator import get_bookstores_key, get_bookstore_key
from bookprices.shared.db.database import Database
from bookprices.shared.model.bookstore import BookStore


class BookStoreService:
    def __init__(self, database: Database, cache: Cache) -> None:
        self._database = database
        self._cache = cache

    def get_bookstores(self) -> list[BookStore]:
        if not (bookstores := self._cache.get(get_bookstores_key())):
            if bookstores := self._database.bookstore_db.get_bookstores():
                self._cache.set(get_bookstores_key(), bookstores)

        return bookstores

    def get_bookstore(self, bookstore_id: int) -> BookStore | None:
        if not (bookstore := self._cache.get(get_bookstore_key(bookstore_id))):
            if bookstore := self._database.bookstore_db.get_bookstore(bookstore_id):
                self._cache.set(get_bookstore_key(bookstore_id), bookstore)

        return bookstore
