import logging
from queue import Queue
from threading import Thread
from typing import Sequence, NamedTuple
from urllib.parse import urlparse

from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.scraper_service import BookStoreScraperService
from bookprices.shared.webscraping.bookstore import BookStoreScraper, BookNotFoundError


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


class BookStoreSearchService:
    _min_searches_per_thread: int = 5

    def __init__(
            self,
            unit_of_work: UnitOfWork,
            cache_key_remover: BookPriceKeyRemover,
            event_manager: EventManager,
            bookstore_scraper_service: BookStoreScraperService,
            thread_count: int) -> None:
        self._unit_of_work = unit_of_work
        self._cache_key_remover = cache_key_remover
        self._event_manager = event_manager
        self._bookstore_scraper_service = bookstore_scraper_service
        self._thread_count = thread_count
        self._book_scrapers: dict[int, BookStoreScraper] = {}
        self._search_queue = Queue()
        self._results = []
        self._logger = logging.getLogger(self.__class__.__name__)

    def search_and_save_books_in_bookstores(self, searches: Sequence[IsbnSearch]) -> None:
        self._create_scrapers()
        self._fill_queue(searches)
        self._start_search()
        self._save_new_urls_and_clear_cache()

    def _create_scrapers(self) -> None:
        self._logger.info("Initializing scrapers...")
        self._book_scrapers.clear()

        self._logger.debug("Getting bookstores from database...")
        with self._unit_of_work as uow:
            bookstores = uow.bookstore_repository.get_list()

        self._logger.debug(f"Found {len(bookstores)} book stores. Creating scrapers...")
        for bookstore in bookstores:
            if bookstore_scraper := self._bookstore_scraper_service.get_scraper(bookstore.id):
                self._book_scrapers[bookstore.id] = bookstore_scraper

        self._logger.info(f"{len(self._book_scrapers)} scrapers created for bookstores.")

    def _start_search(self) -> None:
        if self._search_queue.empty():
            self._logger.info("No searches to process!")
            return
        elif self._search_queue.qsize() / self._thread_count < self._min_searches_per_thread:
            self._logger.info("Starting search using single thread...")
            self._search_books()
        else:
            self._logger.info(f"Starting search using {self._thread_count} threads...")
            threads = []
            for _ in range(self._thread_count):
                thread = Thread(target=self._search_books)
                threads.append(thread)
                thread.start()

            [t.join() for t in threads]

        self._logger.info("Finished search!")

    def _search_books(self) -> None:
        while not self._search_queue.empty():
            try:
                isbn_search = self._search_queue.get()
                if not (scraper := self._book_scrapers.get(isbn_search.bookstore_id)):
                    self._logger.error(f"No book finder found for bookstore id {isbn_search.bookstore_id}.")
                    continue
                if not (search_result := scraper.find_book(book_id=isbn_search.book_id, isbn=isbn_search.isbn)):
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
        with self._unit_of_work as uow:
            uow.bookstore_repository.add_books_to_bookstores(self._results)
        self._logger.debug(f"Saved {result_count} search results to database!")

        self._logger.debug("Removing cache keys for affected books and bookstores...")
        self._remove_cache_for_affected_books_and_bookstores()

        self._logger.debug("Removing results from list...")
        self._results = []

    def _remove_cache_for_affected_books_and_bookstores(self) -> None:
        for result in self._results:
            self._cache_key_remover.remove_keys_for_book(result.book_id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(result.book_id, result.bookstore_id)

    def _fill_queue(self, searches: Sequence[IsbnSearch]) -> None:
        for search in searches:
            self._search_queue.put(search)