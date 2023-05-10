#!/usr/bin/env python3
import logging
import shared
import collections
from urllib.parse import urlparse
from queue import Queue
from threading import Thread

from bookprices.shared.config import loader
from bookprices.shared.db.book import BookDb
from bookprices.shared.db.bookstore import BookStoreDb
from bookprices.shared.webscraping.sitemap import SitemapBookFinder
from bookprices.shared.webscraping.book import BookFinder
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStore


LOG_FILE_NAME = "search_books.log"
MAX_THREADS = 10

BookStoresForBook = collections.namedtuple("BookStoresForBook", ["book", "book_stores"])


class BookStoreSearch:
    def __init__(self, book_db: BookDb, bookstore_db: BookStoreDb, max_thread_count: int):
        self.book_db = book_db
        self.bookstore_db = bookstore_db
        self.max_thread_count = max_thread_count
        self.book_queue = Queue()

    def _get_book_stores_for_book(self, book: Book):
        logging.info(f"Getting book stores with no information for book with id {book.id}...")
        book_stores = []
        for book_store in self.bookstore_db.get_missing_book_stores(book.id):
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
            self.bookstore_db.create_book_store_for_book(book.id, book_store.id, url)
        except Exception as ex:
            logging.error(f"Error while inserting url {url} for book {book.id} and book store {book_store.id}.")
            logging.error(ex)

    def _search_for_next_book(self):
        while not self.book_queue.empty():
            book_stores_for_book = self.book_queue.get()
            for bs in book_stores_for_book.book_stores:
                match_url = BookFinder.search_book_isbn(bs.search_url,
                                                        book_stores_for_book.book.isbn,
                                                        bs.search_result_css_selector)

                if match_url:
                    logging.info(f"Found match for book with id {book_stores_for_book.book.id} in book store with id "
                                 f"{bs.id}: {match_url}")
                    self._create_book_store_for_book(book_stores_for_book.book,
                                                     bs,
                                                     urlparse(match_url).path)

    def _start_search(self):
        logging.info(f"Starting search with {self.max_thread_count} threads...")
        threads = []
        for _ in range(self.max_thread_count):
            t = Thread(target=self._search_for_next_book())
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.info("Finished search!")

    def run(self):
        books = self.book_db.get_books()
        book_stores_for_books = self._get_book_stores_for_books(books)
        self._fill_queue(book_stores_for_books)
        self._start_search()


def main():
    args = shared.parse_arguments()
    configuration = loader.load(args.configuration)
    shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
    books_db = BookDb(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

    bookstore_db = BookStoreDb(configuration.database.db_host,
                               configuration.database.db_port,
                               configuration.database.db_user,
                               configuration.database.db_password,
                               configuration.database.db_name)

    book_search = BookStoreSearch(books_db, bookstore_db, MAX_THREADS)
    book_search.run()


if __name__ == "__main__":
    main()
