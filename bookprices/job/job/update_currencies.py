import logging

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.config.config import Config
from bookprices.shared.service.currency_service import CurrencyService


class UpdateCurrenciesJob(JobBase):
    """ Updates currency exchange rates by fetching the latest data from a public API. """

    def __init__(self, config: Config, currency_service: CurrencyService) -> None:
        super().__init__(config)
        self._currency_service = currency_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self, **kwargs) -> JobResult:
        try:
            self._currency_service.update_rates()
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)
