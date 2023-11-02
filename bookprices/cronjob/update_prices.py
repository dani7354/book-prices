#!/usr/bin/env python3
import logging
import sys
from datetime import datetime
from queue import Queue
from threading import Thread
from bookprices.cronjob import shared
from bookprices.shared.config import loader
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


LOG_FILE_NAME = "update_prices.log"


class PriceUpdateJob:
    def __init__(self, db: Database, thread_count: int):
        self._db = db
        self.thread_count = thread_count
        self._book_stores_queue = Queue()

    def run(self) -> None:
        if not (books := self._db.book_db.get_books()):
            logging.info("No books found")
            return

        if not (book_stores_by_book_id := self._db.bookstore_db.get_book_stores_for_books(books)):
            logging.info("No book stores found for books")
            return

        self._fill_queue(book_stores_by_book_id)
        threads = []
        for _ in range(self.thread_count):
            t = Thread(target=self._get_updated_prices_for_books)
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.info("Done!")

    def _fill_queue(self, book_stores_by_book_id: dict[int, list[BookInBookStore]]) -> None:
        for book_stores in book_stores_by_book_id.values():
            self._book_stores_queue.put(book_stores)

    def _get_updated_prices_for_books(self) -> None:
        while not self._book_stores_queue.empty():
            book_stores_for_book = self._book_stores_queue.get()
            self._get_and_save_prices_for_book(book_stores_for_book)

    def _get_and_save_prices_for_book(self, book_stores: list) -> None:
        new_prices = []
        for book_in_store in book_stores:
            try:
                full_url = book_in_store.get_full_url()
                logging.debug("Getting price for book ID %s at book store ID %s (URL %s)",
                              book_in_store.book.id,
                              book_in_store.book_store.id,
                              full_url)
                new_price_value = get_price(
                    full_url,
                    book_in_store.book_store.price_css_selector,
                    book_in_store.book_store.price_format)
                new_prices.append(
                    BookPrice(0, book_in_store.book, book_in_store.book_store, new_price_value, datetime.now()))
            except PriceSelectorError as ex:
                logging.error(ex)
                self._log_failed_price_update(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.PRICE_SELECT_ERROR)
            except PriceFormatError as ex:
                logging.error(ex)
                self._log_failed_price_update(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.INVALID_PRICE_FORMAT)
            except PriceNotFoundException as ex:
                logging.error(ex)
                self._log_failed_price_update(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.PAGE_NOT_FOUND)
            except PriceFinderConnectionError as ex:
                logging.error(ex)
                self._log_failed_price_update(
                    book_in_store.book.id, book_in_store.book_store.id, FailedUpdateReason.CONNECTION_ERROR)

        if not new_prices:
            logging.warning("No new prices found for book!")
            return

        logging.info("Saving %s new prices", len(new_prices))
        self._db.bookprice_db.create_prices(new_prices)

    def _log_failed_price_update(self, book_id: int, bookstore_id: int, reason: FailedUpdateReason):
        self._db.bookprice_db.create_failed_price_update(
            FailedPriceUpdate(book_id, bookstore_id, reason, datetime.now()))


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        logging.info("Config loaded!")

        db = Database(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

        price_update_job = PriceUpdateJob(db, shared.THREAD_COUNT)
        price_update_job.run()
    except Exception as ex:
        logging.fatal(f"An error occurred while updating prices!")
        logging.fatal(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
