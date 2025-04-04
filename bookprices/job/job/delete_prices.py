import logging
from datetime import date, timedelta
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database


class DeletePricesJob(JobBase):
    """ Deletes price updates for books that are older than a certain number of days. """

    price_max_age_days: ClassVar[int] = 365

    name: ClassVar[str] = "DeletePricesJob"

    def __init__(self, config: Config, db: Database, cache_key_remover: BookPriceKeyRemover) -> None:
        super().__init__(config)
        self._db = db
        self._cache_key_remover = cache_key_remover
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            earliest_date = date.today() - timedelta(days=self.price_max_age_days)
            self._logger.info(f"Deleting prices older than {str(earliest_date)}")

            bookprice_ids = self._db.bookprice_db.get_prices_older_than(earliest_date)
            self._logger.info(f"Found {len(bookprice_ids)} prices to delete")

            ids_to_delete = [bookprice_id.id for bookprice_id in bookprice_ids]
            if not ids_to_delete:
                self._logger.info("No prices to delete!")
                return JobResult(JobExitStatus.SUCCESS)

            self._logger.info("Deleting prices from the database...")
            self._db.bookprice_db.delete_prices(ids_to_delete)

            self._logger.info("Removing cache keys for affected books and bookstores...")
            for ids in bookprice_ids:
                self._cache_key_remover.remove_keys_for_book(ids.book_id)
                self._cache_key_remover.remove_keys_for_book_and_bookstore(ids.book_id, ids.bookstore_id)

            self._logger.info("Prices deleted!")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)
