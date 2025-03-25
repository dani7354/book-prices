import logging
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookInBookStore
from bookprices.shared.model.error import FailedPriceUpdate, FailedUpdateReason
from bookprices.shared.webscraping.price import (
    get_price,
    PriceNotFoundException,
    PriceFinderConnectionError,
    PriceSelectorError,
    PriceFormatError)


class AllPricesUpdateJob(JobBase):
    """ Updates prices for all books in the database. """

    batch_size: ClassVar[int] = 500
    thread_count: ClassVar[int] = 8
    min_updates_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "AllPricesUpdateJob"

    def __init__(self, config: Config, db: Database, cache_key_remover: BookPriceKeyRemover):
        super().__init__(config)
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._book_stores_queue = Queue()
        self._updated_book_prices = []
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        page, offset = 1, 0
        while book_ids := self._db.book_db.get_next_book_ids(offset, self.batch_size):
            book_id_count = len(book_ids)
            self._logger.info(f"Updating prices for {book_id_count} books (page {page})...")
            books = self._db.book_db.get_books_by_ids(book_ids)

            if not (book_stores_by_book_id := self._db.bookstore_db.get_bookstores_for_books(books)):
                self._logger.warning("No book stores found for books!")
                return JobResult(JobExitStatus.SUCCESS)

            self._fill_queue(book_stores_by_book_id)

            self._start_price_update()

            self._save_new_prices_and_clear_cache()
            self._logger.info(f"Finished updating prices for {book_id_count} books (page {page})!")


            page += 1
            offset = (page - 1) * self.batch_size

        return JobResult(JobExitStatus.SUCCESS)

    def _fill_queue(self, book_stores_by_book_id: dict[int, list[BookInBookStore]]) -> None:
        self._logger.debug("Filling book stores for book into queue...")
        for book_stores in book_stores_by_book_id.values():
            self._book_stores_queue.put(book_stores)

    def _start_price_update(self) -> None:
        if self._book_stores_queue.empty():
            self._logger.info("Price update queue is empty!")
        elif self._book_stores_queue.qsize() / self.thread_count < self.min_updates_per_thread:
            self._logger.debug("Updating prices using single thread...")
            self._get_updated_prices_for_books()
        else:
            self._logger.debug("Updating prices using %s threads...", self.thread_count)
            threads = []
            for _ in range(self.thread_count):
                t = Thread(target=self._get_updated_prices_for_books)
                threads.append(t)
                t.start()

            [t.join() for t in threads]

    def _get_updated_prices_for_books(self) -> None:
        while not self._book_stores_queue.empty():
            book_stores_for_book = self._book_stores_queue.get()
            self._get_prices_for_book(book_stores_for_book)

    def _get_prices_for_book(self, book_stores: list) -> None:
        for book_in_store in book_stores:
            try:
                full_url = book_in_store.get_full_url()
                self._logger.debug("Getting price for book ID %s at book store ID %s (URL %s)",
                              book_in_store.book.id,
                              book_in_store.book_store.id,
                              full_url)
                new_price_value = get_price(
                    full_url,
                    book_in_store.book_store.price_css_selector,
                    book_in_store.book_store.price_format)

                self._updated_book_prices.append(
                    BookPrice(id=0,
                              book=book_in_store.book,
                              book_store=book_in_store.book_store,
                              price=new_price_value,
                              created=datetime.now()))
            except PriceSelectorError as ex:
                self._logger.error(ex)
                self._log_failed_price_update_to_db(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.PRICE_SELECT_ERROR)
            except PriceFormatError as ex:
                self._logger.error(ex)
                self._log_failed_price_update_to_db(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.INVALID_PRICE_FORMAT)
            except PriceNotFoundException as ex:
                self._logger.error(ex)
                self._log_failed_price_update_to_db(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.PAGE_NOT_FOUND)
            except PriceFinderConnectionError as ex:
                self._logger.error(ex)
                self._log_failed_price_update_to_db(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.CONNECTION_ERROR)

    def _log_failed_price_update_to_db(self, book_id: int, bookstore_id: int, reason: FailedUpdateReason):
        self._db.bookprice_db.create_failed_price_update(
            FailedPriceUpdate(None, book_id, bookstore_id, reason, datetime.now()))

    def _save_new_prices_and_clear_cache(self) -> None:
        if not self._updated_book_prices:
            self._logger.info("No new price updates to save!")
            return

        self._logger.debug(f"Saving {len(self._updated_book_prices)} new prices")
        self._db.bookprice_db.create_prices(self._updated_book_prices)
        self._logger.info(f"Saved {len(self._updated_book_prices)} new prices")

        self._logger.info("Removing cache keys for affected books and bookstores...")
        for book_price in self._updated_book_prices:
            self._cache_key_remover.remove_keys_for_book(book_price.book.id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(book_price.book.id, book_price.book_store.id)

        self._updated_book_prices.clear()


class BookPricesUpdateJob(JobBase):
    """ Updates prices for specific books. """

    name: ClassVar[str] = "BookPricesUpdateJob"

    def __init__(self, config: Config, db: Database) -> None:
        super().__init__(config)
        self._db = db
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        if not (book_ids := {int(book_id) for book_id in kwargs.get("book_ids", [])}):
            self._logger.error("No valid book ids provided!")
            return JobResult(JobExitStatus.FAILURE)

        # TODO...

        return JobResult(JobExitStatus.SUCCESS)

