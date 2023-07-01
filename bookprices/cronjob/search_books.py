#!/usr/bin/env python3
import logging
from urllib.parse import urlparse
from queue import Queue
from threading import Thread
from typing import NamedTuple
from bookprices.cronjob import shared
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.webscraping.book import BookFinder
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore


LOG_FILE_NAME = "search_books.log"


class BookStoresForBook(NamedTuple):
    book: Book
    book_stores: list[BookStore]


class BookStoreSearch:
    def __init__(self, db: Database, max_thread_count: int):
        self.db = db
        self.max_thread_count = max_thread_count
        self.book_queue = Queue()

    def _get_book_stores_for_book(self, book: Book):
        logging.info(f"Getting book stores with no information for book with id {book.id}...")
        book_stores = []
        for book_store in self.db.bookstore_db.get_missing_book_stores(book.id):
            if book_store.search_url is not None:
                book_stores.append(book_store)

        return book_stores

    def _get_book_stores_for_books(self, books: list) -> list:
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
            self.book_queue.put(book_stores_for_book)

    def _create_book_store_for_book(self, book: Book, book_store: BookStore, url: str):
        try:
            self.db.bookstore_db.create_book_store_for_book(book.id, book_store.id, url)
        except Exception as ex:
            logging.error(f"Error while inserting url {url} for book {book.id} and book store {book_store.id}.")
            logging.error(ex)

    def _search_books(self):
        while not self.book_queue.empty():
            book_stores_for_book = self.book_queue.get()
            for bookstore in book_stores_for_book.book_stores:
                match_url = BookFinder.search_book_isbn(bookstore.search_url,
                                                        book_stores_for_book.book.isbn,
                                                        bookstore.search_result_css_selector)

                if not match_url:
                    continue

                logging.info(f"Found match for book with id {book_stores_for_book.book.id} in book store with id "
                             f"{bookstore.id}: {match_url}")
                self._create_book_store_for_book(book_stores_for_book.book,
                                                 bookstore,
                                                 urlparse(match_url).path)

    def _start_search(self):
        logging.info(f"Starting search with {self.max_thread_count} threads...")
        threads = []
        for _ in range(self.max_thread_count):
            t = Thread(target=self._search_books())
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.info("Finished search!")

    def run(self):
        books = self.db.book_db.get_books()
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
    args = shared.parse_arguments()
    configuration = loader.load(args.configuration)
    shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
    logging.info("Config loaded!")

    logging.info("Starting book search...")
    db = Database(configuration.database.db_host,
                  configuration.database.db_port,
                  configuration.database.db_user,
                  configuration.database.db_password,
                  configuration.database.db_name)

    book_search = BookStoreSearch(db, shared.THREAD_COUNT)
    book_search.run()
    logging.info("Done!")


if __name__ == "__main__":
    main()
