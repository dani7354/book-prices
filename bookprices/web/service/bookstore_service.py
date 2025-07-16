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

    def create(self,
               name: str,
               url: str,
               search_url: str | None,
               search_result_css: str | None,
               image_css: str | None,
               isbn_css: str | None,
               price_css: str | None,
               price_format: str | None,
               color_hex: str | None,
               has_dynamic_content: bool) -> None:
        bookstore = BookStore(
            id=0,
            name=name,
            url=url,
            search_url=search_url,
            search_result_css_selector=search_result_css,
            image_css_selector=image_css,
            isbn_css_selector=isbn_css,
            price_css_selector=price_css,
            price_format=price_format,
            color_hex=color_hex.lower() if color_hex else None,
            has_dynamically_loaded_content=has_dynamic_content)

        self._database.bookstore_db.create_bookstore(bookstore)
        self._cache.delete(get_bookstores_key())

    def update(
            self,
            bookstore_id: int,
            name: str,
            url: str,
            search_url: str | None,
            search_result_css: str | None,
            image_css: str | None,
            isbn_css: str | None,
            price_css: str | None,
            price_format: str | None,
            color_hex: str | None,
            has_dynamic_content: bool) -> None:

        bookstore = BookStore(
            id=bookstore_id,
            name=name,
            url=url,
            search_url=search_url,
            search_result_css_selector=search_result_css,
            image_css_selector=image_css,
            isbn_css_selector=isbn_css,
            price_css_selector=price_css,
            price_format=price_format,
            color_hex=color_hex.lower() if color_hex else None,
            has_dynamically_loaded_content=has_dynamic_content)

        self._database.bookstore_db.update_bookstore(bookstore)
        self._cache.delete(get_bookstores_key())
        self._cache.delete(get_bookstore_key(bookstore_id))

    def delete(self, bookstore_id: int) -> None:
        self._database.bookstore_db.delete_bookstore(bookstore_id)
        self._cache.delete(get_bookstores_key())
        self._cache.delete(get_bookstore_key(bookstore_id))
