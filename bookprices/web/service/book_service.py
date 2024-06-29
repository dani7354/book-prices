from flask_caching import Cache
from bookprices.shared.db.book import BookSearchSortOption, SearchQuery
from bookprices.shared.db.database import Database
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStoreBookPrice, BookInBookStore, BookStore
from bookprices.shared.cache.key_generator import (
    get_authors_key, get_book_list_key, get_book_latest_prices_key, get_book_in_book_store_key, get_book_key,
    get_prices_for_book_in_bookstore_key, get_prices_for_book_key)
from bookprices.web.shared.enum import CacheTtlOption


class BookService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def search(
            self,
            search_phrase: str,
            author: str | None,
            page: int,
            page_size: int,
            sort_option: BookSearchSortOption = BookSearchSortOption.Title,
            descending: bool = False) -> list[Book]:

        query = SearchQuery(
            search_phrase=search_phrase,
            author=author,
            page=page,
            page_size=page_size,
            sort_option=sort_option,
            sort_in_descending_order=descending)

        book_search_function = self._get_search_function(sort_option)
        books_current_cache_key = get_book_list_key(query)
        if not (books := self._cache.get(books_current_cache_key)):
            if books := book_search_function(query):
                self._cache.set(books_current_cache_key, books, timeout=CacheTtlOption.SHORT)

        return books

    def _get_search_function(self, sort_option: BookSearchSortOption) -> callable:
        return self._db.book_db.search_books_with_newest_prices if sort_option == BookSearchSortOption.PriceUpdated \
            else self._db.book_db.search_books

    def get_book(self, book_id: int) -> Book | None:
        cache_key = get_book_key(book_id)
        if not (book := self._cache.get(cache_key)):
            if book := self._db.book_db.get_book(book_id):
                self._cache.set(cache_key, book, timeout=CacheTtlOption.LONG)

        return book

    def get_book_by_isbn(self, isbn: str) -> Book | None:
        return self._db.book_db.get_book_by_isbn(isbn)

    def get_authors(self) -> list[str]:
        if not (authors := self._cache.get(get_authors_key())):
            if authors := self._db.book_db.get_authors():
                self._cache.set(get_authors_key(), authors, timeout=CacheTtlOption.LONG)

        return authors

    def get_latest_prices(self, book_id: int) -> list[BookStoreBookPrice]:
        if not (latest_prices := self._cache.get(get_book_latest_prices_key(book_id))):
            if latest_prices := self._db.bookprice_db.get_latest_prices(book_id):
                self._cache.set(get_book_latest_prices_key(book_id), latest_prices, timeout=CacheTtlOption.MEDIUM)
        return latest_prices

    def get_book_in_bookstore(self, book: Book, bookstore_id: int) -> BookInBookStore | None:
        cache_key = get_book_in_book_store_key(book.id, bookstore_id)
        if not (book_in_bookstore := self._cache.get(cache_key)):
            if book_in_bookstore := self._db.bookstore_db.get_bookstore_for_book(book, bookstore_id):
                self._cache.set(cache_key, book_in_bookstore, timeout=CacheTtlOption.MEDIUM)

        return book_in_bookstore

    def get_prices_for_book_in_bookstore(self, book: Book, bookstore: BookStore) -> list[BookPrice]:
        cache_key = get_prices_for_book_in_bookstore_key(book.id, bookstore.id)
        if not (prices := self._cache.get(cache_key)):
            if prices := self._db.bookprice_db.get_book_prices_for_store(book, bookstore):
                self._cache.set(cache_key, prices, timeout=CacheTtlOption.MEDIUM)

        return prices

    def get_all_prices_for_book(self, book: Book):
        cache_key = get_prices_for_book_key(book.id)
        if not (book_prices := self._cache.get(cache_key)):
            if book_prices := self._db.bookprice_db.get_all_book_prices(book):
                self._cache.set(cache_key, book_prices, timeout=CacheTtlOption.MEDIUM)

        return book_prices

    def create_book(self, book: Book) -> int:
        book_id = self._db.book_db.create_book(book)
        self._cache.delete(get_authors_key())

        return book_id
