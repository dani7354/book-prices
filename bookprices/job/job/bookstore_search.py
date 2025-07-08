import logging
from urllib.parse import urlparse
from queue import Queue
from threading import Thread
from typing import NamedTuple, ClassVar
from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.webscraping.book import BookFinder, BookNotFoundError


class IsbnSearch(NamedTuple):
    """ Used for holding a search for a book in a bookstore. """
    bookstore_id: int
    book_id: int
    isbn: str


class BookStoreBookUrl(NamedTuple):
    """ Used for holding a found book store url for a book before it is written to database. """
    book_id: int
    bookstore_id: int
    url: str


class BookStoreSearchJob(JobBase):
    """ Searches for new books in known bookstores."""

    book_bookstore_batch_size: ClassVar[int] = 500
    min_searches_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "BookStoreSearchJob"

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
        self._book_searchers = {}
        self._search_queue = Queue()
        self._results = []
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Starting searching for book availability in bookstores...")
            self._create_book_finders()
            book_bookstore_offset, book_bookstore_page = 0, 1
            total_searches_count = 0
            while self._get_and_enqueue_next_searches(book_bookstore_offset):
                searches_count_for_batch = self._search_queue.qsize()
                self._logger.info(f"Searches to process {searches_count_for_batch} in this batch...")
                total_searches_count += searches_count_for_batch

                self._start_search()
                self._save_new_urls_and_clear_cache()

                book_bookstore_page += 1
                book_bookstore_offset = (book_bookstore_page - 1) * self.book_bookstore_batch_size

            self._logger.info(f"Total searches_processed: {total_searches_count}")
            self._event_manager.trigger_event(str(BookPricesEvents.BOOKSTORE_SEARCH_COMPLETED))
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)

    def _create_book_finders(self) -> None:
        self._logger.info("Initializing book searchers...")
        self._book_searchers.clear()
        for bookstore in self._db.bookstore_db.get_bookstores():
            self._book_searchers[bookstore.id] = BookFinder(
                bookstore_id=bookstore.id,
                bookstore_name=bookstore.name,
                bookstore_url=bookstore.url,
                search_url=bookstore.search_url,
                bookstore_isbn_css_selector=bookstore.isbn_css_selector,
                search_result_css_selector=bookstore.search_result_css_selector,
                redirects_on_match=not bookstore.search_result_css_selector)

        self._logger.info(f"{len(self._book_searchers)} book finders created for bookstores.")


    def _get_and_enqueue_next_searches(self, offset: int) -> bool:
        for row in self._db.bookstore_db.get_book_isbn_and_missing_bookstores(offset, self.book_bookstore_batch_size):
            self._search_queue.put(
                IsbnSearch(book_id=row["BookId"], bookstore_id=row["BookStoreId"], isbn=row["Isbn"]))

        return not self._search_queue.empty()

    def _start_search(self) -> None:
        if self._search_queue.empty():
            self._logger.info("No searches to process!")
            return
        elif self._search_queue.qsize() / self._thread_count < self.min_searches_per_thread:
            self._logger.info("Starting search using single thread...")
            self._search_books()
        else:
            self._logger.info(f"Starting search using {self._thread_count} threads...")
            threads = []
            for _ in range(self._thread_count):
                thread = Thread(target=self._search_books())
                threads.append(thread)
                thread.start()

            [t.join() for t in threads]

        self._logger.info("Finished search!")

    def _search_books(self) -> None:
        while not self._search_queue.empty():
            try:
                isbn_search = self._search_queue.get()
                if not (book_finder := self._book_searchers.get(isbn_search.bookstore_id)):
                    self._logger.error(f"No book finder found for bookstore id {isbn_search.bookstore_id}.")
                    continue
                if not (search_result := book_finder.find_url_for_book(isbn_search.book_id, isbn_search.isbn)):
                    self._logger.info(
                        f"No search result found for book with id {isbn_search.book_id} "
                        f"and ISBN {isbn_search.isbn} at bookstore {isbn_search.bookstore_id}.")
                    continue
                self._logger.info(
                    f"Found book with id {isbn_search.book_id} at {search_result.url} "
                    f"(bookstore {isbn_search.bookstore_id})")
                self._results.append(
                    BookStoreBookUrl(
                        book_id=search_result.book_id,
                        bookstore_id=search_result.bookstore_id,
                        url=urlparse(search_result.url).path))
            except BookNotFoundError:
                continue
            except Exception as ex:
                self._logger.error(ex)

    def _save_new_urls_and_clear_cache(self) -> None:
        result_count = len(self._results)
        if not result_count:
            self._logger.info("No search results to save!")
            return

        self._logger.info(f"Saving {result_count} search results...")
        self._db.bookstore_db.create_bookstores_for_books(self._results)
        self._logger.debug(f"Saved {result_count} search results to database!")

        self._logger.debug("Removing cache keys for affected books and bookstores...")
        self._remove_cache_for_affected_books_and_bookstores()

        self._logger.debug("Removing results from list...")
        self._results = []

    def _remove_cache_for_affected_books_and_bookstores(self) -> None:
        for result in self._results:
            self._cache_key_remover.remove_keys_for_book(result.book_id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(result.book_id, result.bookstore_id)
