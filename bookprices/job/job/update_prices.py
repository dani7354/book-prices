import logging
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.price_update import PriceUpdateService
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database


class AllBookPricesUpdateJob(JobBase):
    """ Updates prices for all books in the database. """

    batch_size: ClassVar[int] = 500
    thread_count: ClassVar[int] = 8
    min_updates_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "AllPricesUpdateJob"

    def __init__(
            self,
            config: Config,
            db: Database,
            price_update_service: PriceUpdateService):
        super().__init__(config)
        self._db = db
        self._price_update_service = price_update_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            page, offset = 1, 0
            while book_ids := self._db.book_db.get_next_book_ids(offset, self.batch_size):
                book_id_count = len(book_ids)

                self._logger.info(f"Updating prices for {book_id_count} books (page {page})...")
                self._price_update_service.update_prices_for_books(book_ids)
                self._logger.info(f"Finished updating prices for {book_id_count} books (page {page})!")

                page += 1
                offset = (page - 1) * self.batch_size

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)


class BookPricesUpdateJob(JobBase):
    """ Updates prices for specific books. """

    name: ClassVar[str] = "BookPricesUpdateJob"

    def __init__(self, config: Config, price_update_service: PriceUpdateService) -> None:
        super().__init__(config)
        self._price_update_service = price_update_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := [int(book_id) for book_id in kwargs.get("book_ids", [])]):
                self._logger.error("No valid book ids provided!")
                return JobResult(JobExitStatus.FAILURE)

            self._logger.info(f"Updating prices for books {book_ids}...")
            self._price_update_service.update_prices_for_books(book_ids)
            self._logger.info(f"Finished updating prices for books {book_ids}!")

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)
