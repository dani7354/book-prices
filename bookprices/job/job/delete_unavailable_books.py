import logging
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.model.error import FailedUpdateReason
from bookprices.shared.repository.unit_of_work import UnitOfWork


class DeleteUnavailableBooksJob(JobBase):
    """ Job that deletes books if they're no longer available or if the price updates have failed too many times. """

    failed_update_limit: ClassVar[int] = 10

    name: ClassVar[str] = "DeleteBooksJob"

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
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Deleting unavailable books...")
            delete_count = 0
            for book_id, bookstore_id, count in self._list_books_with_failed_updates_exceeding_limit(self.failed_update_limit):
                if self._is_book_unavailable(book_id, bookstore_id, count):
                    delete_count += 1
                    self._logger.info("Deleting book %s from bookstore %s...",book_id, bookstore_id)
                    with self._unit_of_work as uow:
                        uow.bookstore_repository.delete_book_from_bookstore(book_id, bookstore_id)
                        self._logger.info(
                            "Deleting failed price updates for book %s from bookstore %s...",
                            book_id, bookstore_id)
                        uow.failed_price_update_repository.delete_failed_updates(book_id, bookstore_id)

                    self._logger.debug("Removing cache keys for book %s and bookstore %s...",
                                       book_id, bookstore_id)
                    self._cache_key_remover.remove_keys_for_book(book_id)
                    self._cache_key_remover.remove_keys_for_book_and_bookstore(book_id, bookstore_id)
                    self._cache_key_remover.remove_key_for_authors()

            self._logger.info(f"Deleted {delete_count} unavailable books from bookstores!")
            self._event_manager.trigger_event(str(BookPricesEvents.BOOKS_DELETED))
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.exception(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error=ex)

    def _is_book_unavailable(self, book_id: int, bookstore_id: int, count: int) -> bool:
        if count < self.failed_update_limit:
            return False

        with self._unit_of_work as uow:
            failed_price_updates = uow.failed_price_update_repository.get_latest_failed_price_updates(
                book_id, bookstore_id, self.failed_update_limit)
        if len(failed_price_updates) < self.failed_update_limit:
            return False

        return all(f.reason == FailedUpdateReason.PAGE_NOT_FOUND for f in failed_price_updates)

    def _list_books_with_failed_updates_exceeding_limit(self, limit: int) -> list[tuple[int, int, int]]:
        with self._unit_of_work as uow:
            return uow.failed_price_update_repository.get_failed_update_count_above(limit)