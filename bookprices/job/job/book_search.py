import logging
import traceback
from typing import ClassVar, Sequence
from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.enum import ArgumentName
from bookprices.job.service.bookstore_search import IsbnSearch, BookStoreSearchService
from bookprices.shared.config.config import Config
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.repository.unit_of_work import UnitOfWork


class SearchAllMissingBooksInBookStoresJob(JobBase):
    """ Searches for all new books in available bookstores."""

    book_bookstore_batch_size: ClassVar[int] = 500

    name: ClassVar[str] = "SearchAllMissingBooksInBookStoresJob"

    def __init__(
            self,
            config: Config,
            unit_of_work: UnitOfWork,
            event_manager: EventManager,
            bookstore_search_service: BookStoreSearchService) -> None:
        super().__init__(config)
        self._unit_of_work = unit_of_work
        self._event_manager = event_manager
        self._bookstore_search_service = bookstore_search_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Starting searching for book availability in bookstores...")
            book_bookstore_offset, book_bookstore_page = 0, 1
            total_searches_count = 0

            while next_searches := self._get_and_enqueue_next_searches(book_bookstore_offset):
                next_searches_count = len(next_searches)
                self._logger.info(f"Searches to process {next_searches_count} in this batch...")
                self._bookstore_search_service.search_and_save_books_in_bookstores(next_searches)
                total_searches_count += next_searches_count
                book_bookstore_page += 1
                book_bookstore_offset = (book_bookstore_page - 1) * self.book_bookstore_batch_size

            self._event_manager.trigger_event(BookPricesEvents.BOOKSTORE_SEARCH_COMPLETED)
            self._logger.info(f"Total searches_processed: {total_searches_count}")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)

    def _get_and_enqueue_next_searches(self, offset: int) -> list[IsbnSearch]:
        with self._unit_of_work as uow:
            books_and_missing_stores = uow.bookstore_repository.get_book_isbn_and_missing_bookstores(
                offset, self.book_bookstore_batch_size)

        return [
            IsbnSearch(
                book_id=row["BookId"],
                bookstore_id=row["BookStoreId"],
                isbn=row["Isbn"])
            for row in books_and_missing_stores]


class SearchSelectedBooksInBookStoresJob(JobBase):
    """ Job for searching for specific books only. Ids given as arguments """

    name: ClassVar[str] = "SearchSelectedBooksInBookStoresJob"

    def __init__(
            self,
            config: Config,
            unit_of_work: UnitOfWork,
            event_manager: EventManager,
            bookstore_search_service: BookStoreSearchService) -> None:
        super().__init__(config)
        self._unit_of_work = unit_of_work
        self._event_manager = event_manager
        self._bookstore_search_service = bookstore_search_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        if not (book_ids := kwargs.get(ArgumentName.BOOK_IDS)):
            self._logger.error(f"No book ids provided for job {self.name}.")
            return JobResult(exit_status=JobExitStatus.FAILURE)

        if not isinstance(book_ids, list):
            self._logger.error("Invalid argument: book_ids is not a list!")
            return JobResult(exit_status=JobExitStatus.FAILURE)

        isbn_searches = self._get_isbn_searches(book_ids)
        self._bookstore_search_service.search_and_save_books_in_bookstores(isbn_searches)

        self._event_manager.trigger_event(BookPricesEvents.BOOKSTORE_SEARCH_COMPLETED, args=book_ids)

        self._logger.info(f"Search completed for {len(isbn_searches)} books in bookstores.")

        return JobResult(exit_status=JobExitStatus.SUCCESS)

    def _get_isbn_searches(self, book_ids: Sequence) -> list[IsbnSearch]:
        valid_book_ids = []
        for i, book_id in enumerate(book_ids):
            if type(book_id) is not int:
                self._logger.warning(f"Book at index {i} is not an integer. Skipping...")
                continue

            valid_book_ids.append(book_id)
        with self._unit_of_work as uow:
            isbn_numbers_missing_in_stores = uow.bookstore_repository.get_selected_books_and_missing_bookstores(
                valid_book_ids)

        return [
            IsbnSearch(
                book_id=row["BookId"],
                bookstore_id=row["BookStoreId"],
                isbn=row["Isbn"])
            for row in isbn_numbers_missing_in_stores]
