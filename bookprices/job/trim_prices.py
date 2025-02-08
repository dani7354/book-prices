from typing import ClassVar, Sequence
from logging import getLogger, Logger

from bookprices.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.model.bookprice import BookPrice


class TrimPricesJob(JobBase):
    book_ids_batch_size: ClassVar[int] = 500
    min_prices_to_keep: ClassVar[int] = 10

    def __init__(
            self,
            config: Config,
            cache_key_remover: BookPriceKeyRemover,
            bookprice_db: Database,
            logger: Logger) -> None:
        super().__init__(config)
        self._cache_key_remover = cache_key_remover
        self._db = bookprice_db
        self._logger = logger

    def start(self, **kwargs) -> JobResult:
        book_ids_offset, book_id_page = 0, 1
        while book_ids := self._db.book_db.get_next_book_ids(book_ids_offset, self.book_ids_batch_size):
            for book_id in book_ids:
                self.trim_prices_for_book(book_id)

            book_id_page += 1
            book_ids_offset = (book_id_page - 1) * self.book_ids_batch_size

        return JobResult(JobExitStatus.SUCCESS)

    def trim_prices_for_book(self, book_id: int) -> None:
        book = self._db.book_db.get_book_by_id(book_id)
        book_prices_by_book_store = self._db.bookprice_db.get_all_book_prices(book)
        for book_store, prices in book_prices_by_book_store.items():
            self._logger.info(f"Trimming prices for book %s and store %s...", book_id, book_store.id)
            prices_to_delete = self.get_prices_to_remove(prices)

            self._logger.info(
                "Deleting {len(prices_to_delete)} prices for book %s and store %s...",
                book_id, book_store.id)
            self._db.bookprice_db.delete_prices([price.id for price in prices_to_delete])

    def get_prices_to_remove(self, prices: Sequence[BookPrice]) -> list[BookPrice]:
        prices_to_delete = []
        if len(prices) <= self.min_prices_to_keep:
            return prices_to_delete

        last_price = None
        total_prices_count, index = len(prices), 0
        while total_prices_count - len(prices_to_delete) > self.min_prices_to_keep and index < total_prices_count:
            price = prices[index]
            if last_price is None:
                last_price = price
            elif price.price == last_price.price:
                prices_to_delete.append(price)
            else:
                last_price = price
            index += 1

        return prices_to_delete


def start_job(config: Config) -> JobResult:
    cache_key_remover = BookPriceKeyRemover(
        RedisClient(config.cache.host, config.cache.database, config.cache.port))

    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    logger = getLogger(__name__)
    job = TrimPricesJob(config, cache_key_remover, db, logger)

    return job.start()