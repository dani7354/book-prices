#!/usr/bin/env python3
import logging
import sys
from urllib.parse import urlparse
from queue import Queue
from threading import Thread
from typing import NamedTuple
from bookprices.cronjob import shared
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.webscraping.book import BookFinder, IsbnSearch, BookNotFoundError
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore


LOG_FILE_NAME = "search_books.log"


class BookStoresForBook(NamedTuple):
    book: Book
    book_stores: list[BookStore]


class BookStoreSearchJob:
    def __init__(self, db: Database, cache_key_remover: BookPriceKeyRemover, thread_count: int):
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._thread_count = thread_count
        self._book_queue = Queue()

    def _get_book_stores_for_book(self, book: Book) -> list[BookStore]:
        logging.info(f"Getting book stores with no information for book with id {book.id}...")
        book_stores = []
        for book_store in self._db.bookstore_db.get_missing_bookstores(book.id):
            if book_store.search_url is not None:
                book_stores.append(book_store)

        return book_stores

    def _get_book_stores_for_books(self, books: list) -> list[BookStoresForBook]:
        book_stores_for_books = []
        for book in books:
            if not book.isbn:
                logging.warning(f"Book with id {book.id} has no ISBN!")
                continue

            book_stores = self._get_book_stores_for_book(book)
            if len(book_stores) > 0:
                book_stores_for_books.append(BookStoresForBook(book=book, book_stores=book_stores))

        return book_stores_for_books

    def _fill_queue(self, book_stores_for_books: list):
        for book_stores_for_book in book_stores_for_books:
            self._book_queue.put(book_stores_for_book)

    def _create_book_store_for_book(self, book: Book, book_store: BookStore, url: str):
        try:
            logging.debug("Saving new bookstore with ID %s for book %s...", book_store.id, book.id)
            self._db.bookstore_db.create_bookstore_for_book(book.id, book_store.id, url)

            logging.debug("Removing cache keys for book %s and book store %s...", book.id, book_store.id)
            self._cache_key_remover.remove_keys_for_book(book.id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(book.id, book_store.id)
        except Exception as ex:
            logging.error(f"Error while inserting url {url} for book {book.id} and book store {book_store.id}.")
            logging.error(ex)

    def _search_books(self):
        while not self._book_queue.empty():
            book_stores_for_book = self._book_queue.get()
            for bookstore in book_stores_for_book.book_stores:
                try:
                    if not bookstore.isbn_css_selector:
                        logging.warning(f"Book store with id {bookstore.id} has no ISBN CSS selector!")
                        continue

                    search_request = IsbnSearch(bookstore.search_url,
                                                bookstore.search_result_css_selector,
                                                book_stores_for_book.book.isbn,
                                                bookstore.isbn_css_selector,
                                                bookstore.url)

                    match_url = BookFinder.search_book_isbn(search_request)
                    logging.info(f"Found match for book with id {book_stores_for_book.book.id} in book store with id "
                                 f"{bookstore.id}: {match_url}")

                    self._create_book_store_for_book(book_stores_for_book.book,
                                                     bookstore,
                                                     urlparse(match_url).path)
                except BookNotFoundError as ex:
                    logging.error(ex)

    def _start_search(self):
        logging.info(f"Starting search with {self._thread_count} threads...")
        threads = []
        for _ in range(self._thread_count):
            t = Thread(target=self._search_books())
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.info("Finished search!")

    def run(self):
        books = self._db.book_db.get_books()
        if not books:
            logging.info("No books found!")
            return

        book_stores_for_books = self._get_book_stores_for_books(books)
        if not book_stores_for_books:
            logging.info("No book stores found for the existing books!")
            return

        self._fill_queue(book_stores_for_books)
        self._start_search()


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load_from_file(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        logging.info("Config loaded!")

        logging.info("Starting book search...")
        db = Database(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

        cache_key_remover = BookPriceKeyRemover(
            RedisClient(configuration.cache.host, configuration.cache.database, configuration.cache.port))

        book_search = BookStoreSearchJob(db, cache_key_remover, shared.THREAD_COUNT)
        book_search.run()
        logging.info("Done!")
    except Exception as ex:
        logging.error(f"Error searching for books: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
