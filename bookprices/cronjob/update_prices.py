#!/usr/bin/env python3
import logging
import sys
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from bookprices.cronjob import shared
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookInBookStore
from bookprices.shared.webscraping.price import PriceFinder


LOG_FILE_NAME = "update_prices.log"


class PriceUpdateJob:
    def __init__(self, db: Database, thread_count: int):
        self._db = db
        self.thread_count = thread_count
        self._book_stores_queue = Queue()

    def run(self):
        books = self._db.book_db.get_books()
        if not books:
            logging.info("No books found")
            return

        book_stores_by_book_id = self._db.bookstore_db.get_book_stores_for_books(books)
        if not book_stores_by_book_id:
            logging.info("No book stores found for books")
            return

        self._fill_queue(book_stores_by_book_id)
        threads = []
        for _ in range(self.thread_count):
            t = Thread(target=self._get_updated_prices_for_books)
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.info(f"Done!")

    def _fill_queue(self, book_stores_by_book_id: dict[int, list[BookInBookStore]]):
        for book_stores in book_stores_by_book_id.values():
            self._book_stores_queue.put(book_stores)

    def _get_updated_prices_for_books(self):
        while not self._book_stores_queue.empty():
            book_stores_for_book = self._book_stores_queue.get()
            self._get_and_save_prices_for_book(book_stores_for_book)

    def _get_and_save_prices_for_book(self, book_stores: list):
        new_prices = []
        for book_in_store in book_stores:
            full_url = book_in_store.get_full_url()
            try:
                logging.debug(f"Getting price for book ID {book_in_store.book.id} at book store ID "
                              f"{book_in_store.book_store.id} (URL {full_url})")

                new_price_value = PriceFinder.get_price(book_in_store.get_full_url(),
                                                        book_in_store.book_store.price_css_selector,
                                                        book_in_store.book_store.price_format)

                new_prices.append(BookPrice(0,
                                            book_in_store.book,
                                            book_in_store.book_store,
                                            new_price_value,
                                            datetime.now(timezone.utc).isoformat()))
            except Exception as ex:
                logging.error(f"Failed get updated price from {full_url}")
                logging.error(f"Exception: {ex}")

        logging.info(f"Saving {len(new_prices)} new prices")
        self._db.bookprice_db.create_prices(new_prices)


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
        logging.error(f"An error occurred while updating prices!")
        logging.error(f"Exception: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
