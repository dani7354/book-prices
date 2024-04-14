from flask_caching import Cache
from bookprices.shared.db.book import BookSearchSortOption, SearchQuery
from bookprices.shared.db.database import Database
from bookprices.shared.model.book import Book
from bookprices.web.cache.key_generator import get_authors_key, get_book_list_key


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
            books = book_search_function(query)
            self._cache.set(books_current_cache_key, books)

        return books

    def _get_search_function(self, sort_option: BookSearchSortOption) -> callable:
        return self._db.book_db.search_books_with_newest_prices if sort_option == BookSearchSortOption.PriceUpdated \
            else self._db.book_db.search_books

    def get_authors(self) -> list[str]:
        if not (authors := self._cache.get(get_authors_key())):
            authors = self._db.book_db.get_authors()
            self._cache.set(get_authors_key(), authors)

        return authors
