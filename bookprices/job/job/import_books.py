import datetime
import logging
from urllib.parse import urlparse

import queue
from threading import Thread
from typing import ClassVar, NamedTuple

from requests import RequestException

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.db.tables import Book
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.validation import isbn as isbn_validator
from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import RateLimiter, HttpClient


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

    _period_seconds: ClassVar[int] = 1
    _request_count: ClassVar[int] = 1


    def __init__(
            self,
            config: Config,
            unit_of_work: UnitOfWork,
            cache_key_remover: BookPriceKeyRemover,
            event_manager: EventManager) -> None:
        super().__init__(config)
        self._unit_of_work = unit_of_work
        self._cache_key_remover = cache_key_remover
        self._event_manager = event_manager
        self._book_url_queue = queue.Queue()
        self._book_list_url_queue = queue.Queue()
        self._new_books = []
        self._rate_limiter = RateLimiter(self._request_count, self._period_seconds)
        self._logger = logging.getLogger(self.__class__.__name__)

        self._valid_book_formats = {
            "Paperback", "Hardback", "Indbundet", "Hæftet", "Haeftet", "Bog", "Bog med hæftet ryg"}

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Getting book urls...")
            self._enqueue_urls_for_book_list_pages(
                "https://www.williamdam.dk/boeger/skoenlitteratur/romaner/--type_bog,sprog_dansk?p={page}",
                250)

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
                with HttpClient() as http_client:
                    self._rate_limiter.wait_if_needed()
                    book_list_response = http_client.get(book_list_url)
                book_list_content_bs = HtmlContent(book_list_response.text)
                for url in book_list_content_bs.find_elements_by_css_and_get_attribute_values(self._book_url_css, "href"):
                    self._book_url_queue.put(url)
            except RequestException as ex:
                self._logger.error(ex)

    def _get_next_book(self) -> None:
        while not self._book_url_queue.empty():
            try:
                book_url = self._book_url_queue.get()
                with HttpClient() as http_client:
                    self._rate_limiter.wait_if_needed()
                    book_response = http_client.get(book_url)
                book = self._parse_book(book_response.text)
                if self._is_book_valid(book):
                    logging.debug(f"Found valid book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})")
                    self._new_books.append(NewBook(book=book, url=urlparse(book_url).path))
            except (RequestException, ValueError, KeyError) as ex:
                self._logger.error(ex)

    def _create_or_update_books(self) -> None:
        created_count, updated_count = 0, 0
        with self._unit_of_work as uow:
            existing_books_isbn = uow.book_repository.list_books_by_isbn()
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

                    with self._unit_of_work as uow:
                        uow.book_repository.update(updated_book)
                    self._cache_key_remover.remove_keys_for_book(updated_book.id)
                    self._cache_key_remover.remove_key_for_authors()
                    updated_count += 1
                else:
                    self._logger.debug(f"Saving book with ISBN {book.isbn}")
                    with self._unit_of_work as uow:
                        book_id = uow.book_repository.create(book)
                    self._cache_key_remover.remove_key_for_authors()
                    self._cache_key_remover.remove_keys_for_book_and_bookstore(book_id, self._bookstore_id)
                    created_count += 1
                with self._unit_of_work as uow:
                    uow.bookstore_repository.add_book_to_bookstore_if_not_exists(book_id, self._bookstore_id, url)
            except Exception as ex:
                self._logger.error(f"Error while inserting book: {book.title}, {book.author}, {book.isbn}")
                self._logger.error(ex)
        logging.info(f"{created_count} new book(s) saved!")
        logging.info(f"{updated_count} book(s) updated!")

    def _parse_book(self, data: str) -> Book:
        html_content = HtmlContent(data)
        title, author, isbn, format_ = (None, None, None, None)

        title = self._parse_title(html_content)
        if author := html_content.find_element_text_by_css(self._author_css):
            author = author.strip()

        for element in html_content.find_elements_by_css(self._book_details_list_css):
            if "ISBN-13" in element:
                if isbn := HtmlContent(element).find_element_text_by_css("span.detail-value").strip():
                    isbn = isbn.strip()
            if "Format" in element:
                if format_text := HtmlContent(element).find_element_text_by_css("span.detail-value").strip():
                    if format_text in self._valid_book_formats:
                        format_ = format_text

        return Book(isbn=isbn, title=title, author=author, format=format_, created=datetime.datetime.now())

    def _parse_title(self, content: HtmlContent) -> str | None:
        if not (title_element := content.find_element_by_css(self._title_css)):
            return None

        title_content = HtmlContent(title_element)
        title_text = content.find_element_text_by_css(self._title_css)
        if span_text := title_content.find_element_text_by_css("span"):
            title_text = title_text.replace(span_text, "")

        return title_text.strip() if title_text else None

    def _is_book_valid(self, book: Book) -> bool:
        self._logger.debug(f"Validating book: {book.title} ({book.format}) by {book.author} (ISBN-13: {book.isbn})...")
        return book.author and book.title and isbn_validator.check_isbn13(book.isbn) and book.format
