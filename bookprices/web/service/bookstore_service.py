from flask_caching import Cache

from bookprices.shared.cache.key_generator import get_bookstores_key, get_bookstore_key
from bookprices.shared.db.tables import BookStore
from bookprices.shared.repository.unit_of_work import UnitOfWork


class BookStoreService:
    def __init__(self, unit_of_work: UnitOfWork, cache: Cache) -> None:
        self._unit_of_work = unit_of_work
        self._cache = cache

    def get_bookstores(self) -> list[BookStore]:
        if not (bookstores := self._cache.get(get_bookstores_key())):
            with self._unit_of_work as uow:
                if bookstores := uow.bookstore_repository.get_list():
                    self._cache.set(get_bookstores_key(), bookstores)

        return bookstores

    def get_bookstore(self, bookstore_id: int) -> BookStore | None:
        if not (bookstore := self._cache.get(get_bookstore_key(bookstore_id))):
            with self._unit_of_work as uow:
                if bookstore := uow.bookstore_repository.get(bookstore_id):
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
               scraper_id: str | None) -> None:
        bookstore = self._create_bookstore(
            name=name,
            url=url,
            search_url=search_url,
            search_result_css=search_result_css,
            image_css=image_css,
            isbn_css=isbn_css,
            price_css=price_css,
            price_format=price_format,
            color_hex=color_hex,
            scraper_id=scraper_id)

        with self._unit_of_work as uow:
            uow.bookstore_repository.add(bookstore)
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
            scraper_id: str | None) -> None:
        bookstore = self._create_bookstore(
            bookstore_id=bookstore_id,
            name=name,
            url=url,
            search_url=search_url,
            search_result_css=search_result_css,
            image_css=image_css,
            isbn_css=isbn_css,
            price_css=price_css,
            price_format=price_format,
            color_hex=color_hex,
            scraper_id=scraper_id)

        with self._unit_of_work as uow:
            uow.bookstore_repository.update(bookstore)
        self._cache.delete(get_bookstores_key())
        self._cache.delete(get_bookstore_key(bookstore_id))

    def delete(self, bookstore_id: int) -> None:
        with self._unit_of_work as uow:
            uow.bookstore_repository.delete(bookstore_id)
        self._cache.delete(get_bookstores_key())
        self._cache.delete(get_bookstore_key(bookstore_id))

    @staticmethod
    def _create_bookstore(
            name: str,
            url: str,
            search_url: str | None,
            search_result_css: str | None,
            image_css: str | None,
            isbn_css: str | None,
            price_css: str | None,
            price_format: str | None,
            color_hex: str | None,
            scraper_id: str | None,
            bookstore_id: int = 0) -> BookStore:
        return BookStore(
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
            scraper_id=scraper_id)
