#!/usr/bin/env python3
import logging
import requests
import sys
import queue
from bs4 import BeautifulSoup
from threading import Thread
from typing import NamedTuple, Optional
from bookprices.cronjob import shared
from bookprices.shared.config import loader
from bookprices.shared.db.book import BookDb
from bookprices.shared.model.book import Book
from bookprices.shared.validation import isbn as isbn_validator


BOOK_URL_CSS = "a.product-name"
BOOK_DETAILS_LIST_CSS = "ul.list li"
TITLE_CSS = "h1"
AUTHOR_CSS = "h2.author span a"
LOG_FILE_NAME = "import_wdam_books.log"

VALID_BOOK_FORMAT = {"Paperback", "Hardback", "Indbundet", "Hæftet", "Haeftet", "Bog", "Bog med hæftet ryg"}


class BookList(NamedTuple):
    url: str
    page_count: int


list_urls = [BookList("https://www.williamdam.dk/boeger/skoenlitteratur/romaner/--type_bog,sprog_dansk?p={0}", 150)]


class WdamBookImport:
    def __init__(self, db: BookDb, thread_count: int, book_list_urls: list[BookList]):
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
        self._create_or_update_books(books)
        logging.info("Done!")

    def _get_book_urls(self) -> list:
        book_urls = []
        for list_url in self.book_list_urls:
            for page in range(1, list_url.page_count + 1):
                book_list_response = requests.get(list_url.url.format(page))
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
                logging.debug(f"Found valid book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})")
                books.append(book)

    def _create_or_update_books(self, books: list[Book]):
        created_count = 0
        updated_count = 0
        existing_books_isbn = {b.isbn: b for b in self.db.get_books()}
        for book in books:
            try:
                if book.isbn in existing_books_isbn:
                    logging.debug(f"Updating book with ISBN {book.isbn}")
                    existing_book = existing_books_isbn[book.isbn]
                    updated_book = Book(existing_book.id,
                                        book.title,
                                        book.author,
                                        book.format,
                                        existing_book.image_url,
                                        existing_book.created)

                    self.db.update_book(updated_book)
                    updated_count += 1
                else:
                    logging.debug(f"Saving book with ISBN {book.isbn}")
                    self.db.create_book(book)
                    created_count += 1
            except Exception as ex:
                logging.error(f"Error while inserting book: {book.title}, {book.author}, {book.isbn}")
                logging.error(ex)
        logging.info(f"{created_count} new book(s) saved!")
        logging.info(f"{updated_count} book(s) updated!")

    def _parse_book(self, data: str) -> Book:
        data_bs = BeautifulSoup(data, "html.parser")
        title, author, isbn, format_ = (None, None, None, None)

        title = self._parse_title(data_bs)
        format_ = self._parse_format(data_bs)
        author_tag = data_bs.select_one(AUTHOR_CSS)
        if author_tag:
            author = author_tag.get_text().strip()

        for li in data_bs.select(BOOK_DETAILS_LIST_CSS):
            all_text = li.get_text()
            if "ISBN-13" in all_text:
                isbn = li.select_one("span").get_text().strip()

        return Book(0, isbn, title, author, format_, None)

    @staticmethod
    def _is_book_valid(book: Book) -> bool:
        logging.debug(f"Validating book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})...")
        return book.author and book.title and isbn_validator.check_isbn13(book.isbn) and book.format

    @staticmethod
    def _parse_title(data_bs: BeautifulSoup) -> Optional[str]:
        title_tag = data_bs.select_one(TITLE_CSS)
        if not title_tag:
            return None
        title = title_tag.get_text()
        span_tag = title_tag.select_one("span")
        if span_tag:
            span_text = span_tag.get_text()
            title = title.replace(span_text, "")

        return title.strip() if title else None

    @staticmethod
    def _parse_format(data_bs: BeautifulSoup) -> Optional[str]:
        title_tag = data_bs.select_one(TITLE_CSS)
        if not title_tag or not (span_tag := title_tag.select_one("span")):
            return None
        span_text = span_tag.get_text()
        for valid_format in VALID_BOOK_FORMAT:
            if valid_format in span_text:
                return valid_format

        return None


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
