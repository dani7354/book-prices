import logging
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.model.error import FailedUpdateReason, FailedPriceUpdateCount


class DeleteUnavailableBooksJob(JobBase):
    """ Job that deletes books if they're no longer available or if the price updates have failed too many times. """

    failed_update_limit: ClassVar[int] = 3

    name: ClassVar[str] = "DeleteBooksJob"

    def __init__(self, config: Config, db: Database, cache_key_remover: BookPriceKeyRemover):
        super().__init__(config)
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            self._logger.info("Deleting unavailable books...")
            delete_count = 0
            for failed_update_count in self._db.bookprice_db.get_failed_price_update_counts(self.failed_update_limit):
                if self._is_book_unavailable(failed_update_count):
                    delete_count += 1
                    self._logger.info("Deleting book %s from bookstore %s...",
                                      failed_update_count.book_id, failed_update_count.bookstore_id)
                    self._db.bookstore_db.delete_book_from_bookstore(
                        failed_update_count.book_id, failed_update_count.bookstore_id)
                    self._logger.info("Deleting failed price updates for book %s from bookstore %s...",
                                      failed_update_count.book_id, failed_update_count.bookstore_id)
                    self._db.bookprice_db.delete_failed_price_updates(
                        failed_update_count.book_id, failed_update_count.bookstore_id)

                    self._logger.debug("Removing cache keys for book %s and bookstore %s...",
                                       failed_update_count.book_id, failed_update_count.bookstore_id)
                    self._cache_key_remover.remove_keys_for_book(failed_update_count.book_id)
                    self._cache_key_remover.remove_keys_for_book_and_bookstore(
                        failed_update_count.book_id, failed_update_count.bookstore_id)
                    self._cache_key_remover.remove_key_for_authors()

            self._logger.info(f"Deleted {delete_count} unavailable books from bookstores!")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)

    def _is_book_unavailable(self, failed_update_count: FailedPriceUpdateCount):
        if failed_update_count.count < self.failed_update_limit:
            return False

        failed_price_updates = self._db.bookprice_db.get_latest_failed_price_updates(
            failed_update_count.book_id, failed_update_count.bookstore_id, self.failed_update_limit)
        if len(failed_price_updates) < self.failed_update_limit:
            return False

        return all(f.reason == FailedUpdateReason.PAGE_NOT_FOUND for f in failed_price_updates)
