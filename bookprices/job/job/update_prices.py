import logging
import traceback
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.enum import JobRunArgumentName
from bookprices.job.service.price_update import PriceUpdateService
from bookprices.shared.config.config import Config
from bookprices.shared.event.base import EventManager
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.repository.unit_of_work import UnitOfWork


class AllBookPricesUpdateJob(JobBase):
    """ Updates prices for all books. """

    batch_size: ClassVar[int] = 500

    name: ClassVar[str] = "AllBookPricesUpdateJob"

    def __init__(
            self,
            config: Config,
            unit_of_work: UnitOfWork,
            price_update_service: PriceUpdateService,
            event_manager: EventManager) -> None:
        super().__init__(config)
        self._unit_of_work = unit_of_work
        self._price_update_service = price_update_service
        self._event_manager = event_manager
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            page, offset = 1, 0
            while book_ids := self._get_next_book_ids(offset, self.batch_size):
                book_id_count = len(book_ids)

                self._logger.info(f"Updating prices for {book_id_count} books (page {page})...")
                self._price_update_service.update_prices_for_books(book_ids)
                self._logger.info(f"Finished updating prices for {book_id_count} books (page {page})!")

                page += 1
                offset = (page - 1) * self.batch_size

            self._event_manager.trigger_event(str(BookPricesEvents.BOOK_PRICES_UPDATED))

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(JobExitStatus.FAILURE, error_message=ex)

    def _get_next_book_ids(self, offset: int, limit: int) -> list[int]:
        with self._unit_of_work as uow:
            return uow.book_repository.list_book_ids(offset, limit)


class  SelectedBookPricesUpdateJob(JobBase):
    """ Updates prices for selected books """

    name: ClassVar[str] = "SelectedBookPricesUpdateJob"

    def __init__(
            self, 
            config: Config,
            price_update_services: PriceUpdateService,
            event_manager: EventManager) -> None:
        super().__init__(config)
        self._price_update_service = price_update_services
        self._event_manager = event_manager
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := kwargs.get(JobRunArgumentName.BOOK_IDS)):
                self._logger.error(f"No book ids given for {self.name}!")
                return JobResult(JobExitStatus.FAILURE, error_message=ValueError("No book ids given!"))

            if not (isinstance(book_ids, list)) or not all(isinstance(book_id, int) for book_id in book_ids):
                self._logger.error("Invalid arguments: book_ids is not a list of integers!")
                return JobResult(
                    exit_status=JobExitStatus.FAILURE,
                    error_message=ValueError(f"Invalid argument type for {JobRunArgumentName.BOOK_IDS}"))

            book_id_count = len(book_ids)
            self._logger.info(f"Updating prices for {book_id_count} books...")
            self._price_update_service.update_prices_for_books(book_ids)
            self._logger.info(f"Finished updating prices for {book_id_count} books.")

            self._event_manager.trigger_event(str(BookPricesEvents.BOOK_PRICES_UPDATED), book_ids=book_ids)

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.exception(ex)
            return JobResult(JobExitStatus.FAILURE, error_message=ex)