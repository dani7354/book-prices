import logging
from typing import ClassVar
from logging import getLogger

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.argument_service import JobRunArgumentName, JobRunArgumentService
from bookprices.job.service.trim_prices_service import TrimPricesService
from bookprices.job.shared.error_message import FAILED_TO_PARSE_ARGUMENTS
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.repository.unit_of_work import UnitOfWork


class TrimAllPricesJob(JobBase):
    """
    Trims prices for all books in the database.
    It removes duplicate prices for saving disk space and improving performance.
    """

    book_ids_batch_size: ClassVar[int] = 500


    name: ClassVar[str] = "TrimAllPricesJob"

    def __init__(
            self,
            config: Config,
            cache_key_remover: BookPriceKeyRemover,
            unit_of_work: UnitOfWork,
            trim_prices_service: TrimPricesService) -> None:
        super().__init__(config)
        self._cache_key_remover = cache_key_remover
        self._unit_of_work = unit_of_work
        self._trim_prices_service = trim_prices_service
        self._logger = getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            book_ids_offset, book_id_page = 0, 1
            while book_ids := self._list_book_ids(book_ids_offset, self.book_ids_batch_size):
                for book_id in book_ids:
                    self._trim_prices_service.trim_prices_for_book(book_id)

                book_id_page += 1
                book_ids_offset = (book_id_page - 1) * self.book_ids_batch_size

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.exception(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error=ex)

    def _list_book_ids(self, offset: int, limit: int) -> list[int]:
        with self._unit_of_work as uow:
            return uow.book_repository.list_book_ids(offset, limit)


class TrimSelectedPricesJob(JobBase):
    """
    Trims prices for selected books in the database.
    It removes duplicate prices for saving disk space and improving performance. Book ids given as argument.
    """

    name: ClassVar[str] = "TrimSelectedPricesJob"

    def __init__(
            self,
            config: Config,
            trim_prices_service: TrimPricesService,
            argument_service: JobRunArgumentService,
            cache_key_remover: BookPriceKeyRemover):
        super().__init__(config)
        self._trim_prices_service = trim_prices_service
        self._argument_service = argument_service
        self._cache_key_remover = cache_key_remover
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := self._argument_service.parse_argument(JobRunArgumentName.BOOK_IDS, **kwargs)):
                self._logger.error(f"Failed to parse book ids for {self.name}!")
                return JobResult(JobExitStatus.FAILURE, error=ValueError(FAILED_TO_PARSE_ARGUMENTS))

            self._logger.info(f"Trimming prices for {len(book_ids)} books...")
            for book_id in book_ids:
                self._trim_prices_service.trim_prices_for_book(book_id)

            self._logger.info("Finished trimming prices for selected books!")

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.exception(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error=ex)
