import logging
import time
from threading import Thread
from typing import ClassVar

import schedule

from bookprices.job.job.book_search import BookStoreSearchJob
from bookprices.job.job.delete_images import DeleteImagesJob
from bookprices.job.job.delete_unavailable_books import DeleteUnavailableBooksJob
from bookprices.job.job.download_images import DownloadImagesJob
from bookprices.job.job.import_books import WilliamDamBookImportJob
from bookprices.job.job.update_prices import AllBookPricesUpdateJob
from bookprices.shared.service.job_service import (
    JobService, JobSchemaFields, JobRunPriority, CreationFailedError, JobSourceUnavailableError)
from bookprices.job.job.trim_prices import TrimPricesJob


class JobScheduler:
    job_run_priority: ClassVar[str] = JobRunPriority.NORMAL.value
    time_zone: ClassVar[str] = "Europe/Copenhagen"

    def __init__(self, job_service: JobService) -> None:
        self._job_service = job_service
        self._logger = logging.getLogger(__name__)
        self._available_jobs = {}

    def start(self) -> None:
        self._logger.info("Starting job scheduler...")
        self._set_available_jobs()
        self.schedule_jobs()
        running = True
        while running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self._logger.info("Received keyboard interrupt. Exiting...")
                running = False
            except JobSourceUnavailableError as e:
                self._logger.error(f"Job API is unavailable: {e}. Exiting...")
                running = False
            except Exception as ex:
                self._logger.error(f"Error while sending start request: {ex}")

        self._logger.info("Job scheduler stopped.")

    def schedule_jobs(self) -> None:
        schedule.every().day.at("01:00", self.time_zone).do(self._set_available_jobs)

        schedule.every().day.at("02:00", self.time_zone).do(
            self._send_start_job_request, DeleteUnavailableBooksJob.name)
        schedule.every().day.at("05:00", self.time_zone).do(
            self._send_start_job_request, WilliamDamBookImportJob.name)
        schedule.every().day.at("06:00", self.time_zone).do(
            self._send_start_job_request, BookStoreSearchJob.name)
        schedule.every().day.at("07:00", self.time_zone).do(
            self._send_start_job_request, DeleteImagesJob.name)
        schedule.every().day.at("08:00", self.time_zone).do(
            self._send_start_job_request, DownloadImagesJob.name)
        schedule.every().monday.at("10:00", self.time_zone).do(
            self._send_start_job_request, TrimPricesJob.name)
        schedule.every().day.at("11:00", self.time_zone).do(
            self._send_start_job_request, AllBookPricesUpdateJob.name)

    def _set_available_jobs(self):
        self._logger.debug("Getting available jobs...")
        jobs = self._job_service.get_job_list()
        self._available_jobs = {job[JobSchemaFields.NAME.value]: job[JobSchemaFields.ID.value] for job in jobs}

    def _send_start_job_request(self, job_name: str) -> None:
        self._logger.info(f"Starting job {job_name} in a new thread...")
        thread = Thread(target=self._create_job_run_for_job, args=(job_name,))
        thread.start()

    def _create_job_run_for_job(self, job_name: str) -> None:
        try:
            if not (job_id := self._available_jobs.get(job_name)):
                self._logger.warning(f"Job {job_name} not available")
                return
            self._logger.info(f"Creating job run for {job_name}...")
            self._job_service.create_job_run(job_id, self.job_run_priority)
        except CreationFailedError as ex:
            self._logger.error(f"Error while creating job run for {job_name}: {ex}")
