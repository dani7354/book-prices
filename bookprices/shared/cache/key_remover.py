from bookprices.shared.cache.client import CacheClient
from bookprices.shared.cache import key_generator


class BookPriceKeyRemover:
    def __init__(self, cache: CacheClient):
        self._cache = cache

    def remove_keys_for_book(self, book_id: int) -> None:
        keys = [
            key_generator.get_book_key(book_id),
            key_generator.get_book_latest_prices_key(book_id),
            key_generator.get_prices_for_book_key(book_id)
        ]
        self._cache.delete_keys(keys)

    def remove_keys_for_book_and_bookstore(self, book_id: int, bookstore_id: int) -> None:
        keys = [
            key_generator.get_prices_for_book_in_bookstore_key(book_id, bookstore_id),
            key_generator.get_book_in_book_store_key(book_id, bookstore_id)
        ]
        self._cache.delete_keys(keys)

    def remove_key_for_authors(self) -> None:
        key = key_generator.get_authors_key()
        self._cache.delete_key(key)
