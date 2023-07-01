#!/usr/bin/env python3
import logging
import requests
import sys
import queue
from bs4 import BeautifulSoup
from threading import Thread
from bookprices.cronjob import shared
from bookprices.shared.config import loader
from bookprices.shared.db.book import BookDb
from bookprices.shared.model.book import Book
from bookprices.shared.validation import isbn


BOOK_URL_CSS = "a.product-name"
BOOK_DETAILS_LIST_CSS = "ul.list li"
TITLE_CSS = "h1"
AUTHOR_CSS = "h2.author span a"

LOG_FILE_NAME = "import_wdam_books.log"

list_urls = ["https://www.williamdam.dk/boger-i-fokus?n=60",
             "https://www.williamdam.dk/boeger/--type_bog,sprog_dansk?n=60",
             "https://www.williamdam.dk/boeger/skoenlitteratur-og-relaterede-emner/historiske-romaner/--type_bog,sprog"
             "_dansk?orderby=release_date&orderway=desc&n=60"]


class WdamBookImport:
    def __init__(self, db: BookDb, thread_count: int, book_list_urls: list[str]):
        self.db = db
        self.thread_count = thread_count
        self.book_list_urls = book_list_urls
        self.book_url_queue = queue.Queue()

    def run(self):
        logging.info("Getting book urls...")
        book_urls = self._get_book_urls()
        logging.debug(f"{len(book_urls)} URLs found!")

        self._fill_queue(book_urls)

        logging.info(f"Importing books from {len(book_urls)} URLs")
        books = self._get_books()

        logging.info("Saving books...")
        self._save_books_if_not_exist(books)
        logging.info("Done!")

    def _get_book_urls(self) -> list:
        book_urls = []
        for list_url in self.book_list_urls:
            book_list_response = requests.get(list_url)
            if not book_list_response.ok:
                continue

            book_list_bs = BeautifulSoup(book_list_response.content.decode(), "html.parser")
            book_urls_for_list = [t["href"] for t in book_list_bs.select(BOOK_URL_CSS)]
            book_urls.extend(book_urls_for_list)

        return book_urls

    def _fill_queue(self, book_urls: list):
        for u in book_urls:
            self.book_url_queue.put(u)

    def _get_books(self) -> list:
        books = []
        threads = []
        for _ in range(self.thread_count):
            t = Thread(target=self._get_next_book, args=(books,))
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.debug(f"{len(books)} books found!")

        return books

    def _get_next_book(self, books: list):
        while not self.book_url_queue.empty():
            url = self.book_url_queue.get()
            response = requests.get(url)
            if not response.ok:
                continue

            book = self._parse_book(response.content.decode())
            if self._is_book_valid(book):
                logging.debug(f"Found valid book: {book.title} by {book.author} (ISBN-13: {book.isbn})")
                books.append(book)

    def _save_books_if_not_exist(self, books):
        saved_count = 0
        existing_books_isbn = {b.isbn for b in self.db.get_books()}
        for b in books:
            if b.isbn in existing_books_isbn:
                continue
            try:
                logging.debug(f"Saving book with ISBN {b.isbn}")
                self.db.create_book(b)
                saved_count += 1
            except Exception as ex:
                logging.error(f"Error while inserting book: {b.title}, {b.author}, {b.isbn}")
                logging.error(ex)
        logging.info(f"{saved_count} new book(s) saved!")

    def _parse_book(self, data: str) -> Book:
        data_bs = BeautifulSoup(data, "html.parser")
        title, author, isbn = (None, None, None)

        title = self._parse_title(data_bs)
        author_tag = data_bs.select_one(AUTHOR_CSS)
        if author_tag:
            author = author_tag.get_text().strip()

        for li in data_bs.select(BOOK_DETAILS_LIST_CSS):
            all_text = li.get_text()
            if "ISBN-13" in all_text:
                isbn = li.select_one("span").get_text().strip()

        return Book(0, isbn, title, author, None)

    @staticmethod
    def _is_book_valid(book: Book) -> bool:
        return book.author and book.title and isbn.check_isbn13(book.isbn)

    @staticmethod
    def _parse_title(data_bs: BeautifulSoup) -> str:
        title = None
        title_tag = data_bs.select_one(TITLE_CSS)
        if title_tag:
            title = title_tag.get_text()
            span_tag = title_tag.select_one("span")
            if span_tag:
                span_text = span_tag.get_text()
                title = title.replace(span_text, "")

        return title.strip() if title else None


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        books_db = BookDb(configuration.database.db_host,
                          configuration.database.db_port,
                          configuration.database.db_user,
                          configuration.database.db_password,
                          configuration.database.db_name)

        book_import = WdamBookImport(books_db, shared.THREAD_COUNT, list_urls)
        book_import.run()
    except Exception as ex:
        logging.error(f"Failed to import books: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
