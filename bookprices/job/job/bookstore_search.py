import logging
from urllib.parse import urlparse
from queue import Queue
from threading import Thread
from typing import NamedTuple, ClassVar
from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.webscraping.book import BookFinder, IsbnSearch, BookNotFoundError


class BookStoreBookUrl(NamedTuple):
    """ Used for holding a found book store url for a book before it is written to database. """
    book_id: int
    bookstore_id: int
    url: str


class BookStoreSearchJob(JobBase):
    """ Searches for new books in known bookstores."""

    book_bookstore_batch_size: ClassVar[int] = 500
    thread_count: ClassVar[int] = 8
    min_searches_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "BookStoreSearchJob"

    def __init__(self, config: Config, db: Database, cache_key_remover: BookPriceKeyRemover) -> None:
        super().__init__(config)
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._search_queue = Queue()
        self._results = []
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Starting searching for book availability in bookstores...")
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
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)

    def _get_and_enqueue_next_searches(self, offset: int) -> bool:
        for row in self._db.bookstore_db.get_book_isbn_and_missing_bookstores(offset, self.book_bookstore_batch_size):
            self._search_queue.put(
                IsbnSearch(
                    book_id=row["BookId"],
                    bookstore_id=row["BookStoreId"],
                    search_url=row["SearchUrl"],
                    match_css_selector=row["SearchResultCssSelector"],
                    isbn=row["Isbn"],
                    isbn_css_selector=row["IsbnCssSelector"],
                    store_url=row["Url"]))

        return not self._search_queue.empty()

    def _start_search(self):
        if self._search_queue.empty():
            self._logger.info("No searches to process!")
            return
        elif self._search_queue.qsize() / self.thread_count < self.min_searches_per_thread:
            self._logger.info("Starting search using single thread...")
            self._search_books()
        else:
            self._logger.info(f"Starting search using {self.thread_count} threads...")
            threads = []
            for _ in range(self.thread_count):
                thread = Thread(target=self._search_books())
                threads.append(thread)
                thread.start()

            [t.join() for t in threads]

        logging.info("Finished search!")

    def _search_books(self):
        while not self._search_queue.empty():
            try:
                isbn_search = self._search_queue.get()
                match_url = BookFinder.search_book_isbn(isbn_search)
                # Should return none if no book found instead of raising exceptions.
                logging.info(f"Found book with id {isbn_search.book_id} at {match_url} (bookstore {isbn_search.bookstore_id})")
                self._results.append(
                    BookStoreBookUrl(
                        book_id=isbn_search.book_id,
                        bookstore_id=isbn_search.bookstore_id,
                        url=urlparse(match_url).path))
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
        self._results.clear()

    def _remove_cache_for_affected_books_and_bookstores(self) -> None:
        for result in self._results:
            self._cache_key_remover.remove_keys_for_book(result.book_id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(result.book_id, result.bookstore_id)
