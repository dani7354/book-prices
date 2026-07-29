import logging
from datetime import datetime
from typing import ClassVar

from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.repository.unit_of_work import UnitOfWork


class TrimPricesService:
    """ Service for the trim prices job(s) """

    min_prices_to_keep: ClassVar[int] = 10

    def __init__(self, unit_of_work: UnitOfWork, cache_key_remover: BookPriceKeyRemover) -> None:
        self._unit_of_work = unit_of_work
        self._cache_key_remover = cache_key_remover
        self._logger = logging.getLogger(self.__class__.__name__)

    def trim_prices_for_book(self, book_id: int) -> None:
        with self._unit_of_work as uow:
            book = uow.book_repository.get(book_id)
            if not book:
                self._logger.debug(f"No book with id {book_id} in database")
                return

            bookprices_by_bookstore_id = uow.bookprice_repository.get_prices_for_book_by_bookstore_id(book.id)
        for bookstore_id, prices in bookprices_by_bookstore_id.items():
            self._logger.info(f"Trimming prices for book {book_id} and store {bookstore_id}...")
            prices_to_delete = self.get_prices_to_remove(prices)
            if not prices_to_delete:
                self._logger.debug(f"No prices to delete for book {book_id} and store {bookstore_id}")
                continue

            self._logger.info(
                f"Deleting {len(prices_to_delete)} prices for book {book_id} and store {bookstore_id}...")

            with self._unit_of_work as uow:
                uow.bookprice_repository.delete_prices([price[0] for price in prices_to_delete])

            self._cache_key_remover.remove_keys_for_book(book_id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(book_id, bookstore_id)

    def get_prices_to_remove(
            self,
            prices: list[tuple[int, int, int, float, datetime]]) -> list[tuple[int, int, int, float, datetime]]:
        prices_to_delete = []
        if len(prices) <= self.min_prices_to_keep:
            return prices_to_delete

        last_price = None
        total_prices_count, index = len(prices), 0
        while total_prices_count - len(prices_to_delete) > self.min_prices_to_keep and index < total_prices_count:
            price = prices[index]
            if last_price is None:
                last_price = price
            elif price[3] == last_price[3]:
                prices_to_delete.append(price)
            else:
                last_price = price
            index += 1

        return prices_to_delete