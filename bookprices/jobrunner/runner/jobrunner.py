import time
from logging import getLogger
from typing import ClassVar

from bookprices.jobrunner.job.base import JobResult
from bookprices.jobrunner.job.trim_prices import TrimPricesJob
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config, Database


class JobRunner:
    sleep_time_seconds: ClassVar[int] = 5

    def __init__(self, config: Config) -> None:
        self._config = config
        self._jobs = {
            TrimPricesJob.name: self._run_trim_prices_job
        }
        self._logger = getLogger(__name__)

    def start(self) -> None:
        self._logger.info("Starting job runner...")
        running = True
        while running:
            try:
                if next_job := self.get_next_job():
                    self.run_job(next_job)
                else:
                    time.sleep(self.sleep_time_seconds)
            except KeyboardInterrupt:
                self._logger.info("Received keyboard interrupt. Exiting...")
                running = False

    def run_job(self, job: dict) -> None:  # TODO: run in another process!
        job_name = job["name"]
        job_args = job["args"]
        job_func = self._jobs.get(job_name)
        if job_func:
            job_func(**job_args)
        else:
            self._logger.warning(f"Job {job_name} not found!")

    def get_next_job(self) -> dict:
        pass

    def _run_trim_prices_job(self, **kwargs) -> JobResult:
        cache_key_remover = BookPriceKeyRemover(
            RedisClient(
                self._config.cache.host,
                self._config.cache.database,
                self._config.cache.port))

        db = Database(
            self._config.database.db_host,
            self._config.database.db_port,
            self._config.database.db_user,
            self._config.database.db_password,
            self._config.database.db_name)

        job = TrimPricesJob(self._config, cache_key_remover, db)

        return job.start()



