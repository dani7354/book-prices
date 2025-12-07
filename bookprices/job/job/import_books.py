import logging
from urllib.parse import urlparse

import requests
import queue
from bs4 import BeautifulSoup
from threading import Thread
from typing import ClassVar, NamedTuple

from requests import RequestException

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.model.book import Book
from bookprices.shared.validation import isbn as isbn_validator


class NewBook(NamedTuple):
    book: Book
    url: str


class WilliamDamBookImportJob(JobBase):
    """ Imports books from WilliamDam.dk """

    name: ClassVar[str] = "WilliamDamBookImportJob"
    _book_url_css: ClassVar[str] = "a.product-name"
    _book_details_list_css: ClassVar[str] = "ul.list li"
    _title_css: ClassVar[str] = "h1"
    _author_css: ClassVar[str] = "a.manufacturer-link"
    _bookstore_id: ClassVar[int] = 2

    def __init__(
            self,
            config: Config,
            db: Database,
            cache_key_remover: BookPriceKeyRemover,
            event_manager: EventManager) -> None:
        super().__init__(config)
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._event_manager = event_manager
        self._book_url_queue = queue.Queue()
        self._book_list_url_queue = queue.Queue()
        self._new_books = []
        self._logger = logging.getLogger(self.__class__.__name__)

        self._valid_book_formats = {
            "Paperback", "Hardback", "Indbundet", "Hæftet", "Haeftet", "Bog", "Bog med hæftet ryg"}

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Getting book urls...")
            self._enqueue_urls_for_book_list_pages(
                "https://www.williamdam.dk/boeger/skoenlitteratur/romaner/--type_bog,sprog_dansk?p={page}",
                500)

            if self._book_list_url_queue.empty():
                self._logger.info("No book list urls found!")
                return JobResult(JobExitStatus.SUCCESS)

            self._get_book_urls()
            if self._book_url_queue.empty():
                self._logger.info("No book urls found!")
                return JobResult(JobExitStatus.SUCCESS)

            self._logger.info(f"Importing books from {self._book_url_queue.qsize()} URLs")
            self._get_new_books()
            if not self._new_books:
                self._logger.info("No new books found!")
                return JobResult(JobExitStatus.SUCCESS)

            logging.info("Saving books...")
            self._create_or_update_books()
            logging.info("Done!")

            self._event_manager.trigger_event(str(BookPricesEvents.BOOKS_IMPORTED))

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)

    def _get_book_urls(self) -> None:
        self._logger.info(
            f"Getting book urls from {self._book_list_url_queue.qsize()} pages using {self._thread_count} threads...")
        threads = []
        for _ in range(self._thread_count):
            t = Thread(target=self._get_next_book_urls_from_list)
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        self._logger.debug(f"{self._book_url_queue.qsize()} URLs found!")

    def _enqueue_urls_for_book_list_pages(self, book_list_base_url: str, page_count: int) -> None:
        for page_number in range(1, page_count + 1):
            self._book_list_url_queue.put(book_list_base_url.format(page=page_number))

    def _get_new_books(self) -> None:
        threads = []
        for _ in range(self._thread_count):
            t = Thread(target=self._get_next_book)
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        logging.debug(f"{len(self._new_books)} books found!")

    def _get_next_book_urls_from_list(self) -> None:
        while not self._book_list_url_queue.empty():
            try:
                book_list_url = self._book_list_url_queue.get()
                book_list_response = requests.get(book_list_url)
                book_list_response.raise_for_status()
                book_list_content_bs = BeautifulSoup(book_list_response.content.decode(), "html.parser")
                for url_tag in book_list_content_bs.select(self._book_url_css):
                    self._book_url_queue.put(url_tag["href"])
            except RequestException as ex:
                self._logger.error(ex)

    def _get_next_book(self) -> None:
        while not self._book_url_queue.empty():
            try:
                book_url = self._book_url_queue.get()
                book_response = requests.get(book_url)
                book_response.raise_for_status()
                book = self._parse_book(book_response.content.decode())
                if self._is_book_valid(book):
                    logging.debug(f"Found valid book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})")
                    self._new_books.append(NewBook(book=book, url=urlparse(book_url).path))
            except (RequestException, ValueError, KeyError) as ex:
                self._logger.error(ex)

    def _create_or_update_books(self) -> None:
        created_count, updated_count = 0, 0
        existing_books_isbn = {b.isbn: b for b in self._db.book_db.get_books()}
        for book, url in self._new_books:
            try:
                if existing_book := existing_books_isbn.get(book.isbn):
                    self._logger.debug(f"Updating book with ISBN {book.isbn}")
                    book_id = existing_book.id
                    updated_book = Book(id=existing_book.id,
                                        isbn=existing_book.isbn,
                                        title=book.title,
                                        author=book.author,
                                        format=book.format,
                                        image_url=existing_book.image_url,
                                        created=existing_book.created)

                    self._db.book_db.update_book(updated_book)
                    self._cache_key_remover.remove_keys_for_book(updated_book.id)
                    self._cache_key_remover.remove_key_for_authors()
                    updated_count += 1
                else:
                    self._logger.debug(f"Saving book with ISBN {book.isbn}")
                    book_id = self._db.book_db.create_book(book)
                    self._cache_key_remover.remove_key_for_authors()
                    self._cache_key_remover.remove_keys_for_book_and_bookstore(book_id, self._bookstore_id)
                    created_count += 1

                self._db.bookstore_db.create_bookstore_for_book_if_not_exists(book_id, self._bookstore_id, url)
            except Exception as ex:
                self._logger.error(f"Error while inserting book: {book.title}, {book.author}, {book.isbn}")
                self._logger.error(ex)
        logging.info(f"{created_count} new book(s) saved!")
        logging.info(f"{updated_count} book(s) updated!")

    def _parse_book(self, data: str) -> Book:
        data_bs = BeautifulSoup(data, "html.parser")
        title, author, isbn, format_ = (None, None, None, None)

        title = self._parse_title(data_bs)
        author_tag = data_bs.select_one(self._author_css)
        if author_tag:
            author = author_tag.get_text().strip()

        for li in data_bs.select(self._book_details_list_css):
            all_text = li.get_text()
            if "ISBN-13" in all_text:
                isbn = li.select_one("span.detail-value").get_text().strip()
            if "Format" in all_text:
                format_value = li.select_one("span.detail-value").get_text().strip()
                if format_value in self._valid_book_formats:
                    format_ = format_value

        return Book(0, isbn, title, author, format_, None)

    def _parse_title(self, data_bs: BeautifulSoup) -> str | None:
        if not (title_tag := data_bs.select_one(self._title_css)):
            return None
        title = title_tag.get_text()
        if span_tag := title_tag.select_one("span"):
            span_text = span_tag.get_text()
            title = title.replace(span_text, "")

        return title.strip() if title else None

    def _is_book_valid(self, book: Book) -> bool:
        self._logger.debug(f"Validating book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})...")
        return book.author and book.title and isbn_validator.check_isbn13(book.isbn) and book.format
