import time
from logging import getLogger
from typing import ClassVar, Sequence
from collections import Counter

from bookprices.job.job.base import JobExitStatus, JobBase
from bookprices.job.runner.service import RunnerJobService, JobRun
from bookprices.shared.config.config import Config
from bookprices.shared.service.job_service import UpdateFailedError, JobRunStatus, FailedToGetJobRunsError


class JobRunner:
    sleep_time_seconds: ClassVar[int] = 10
    job_run_lookup_max_retries: ClassVar[int] = 3

    def __init__(self, config: Config, job: Sequence[JobBase], job_service: RunnerJobService) -> None:
        self._config = config
        self._job_service = job_service
        self._logger = getLogger(__name__)
        self._jobs = {job.name: job for job in job}
        self._job_lookup_errors = Counter()

    def start(self) -> None:
        self._logger.info("Starting job runner...")
        running = True
        while running:
            try:
                if next_job := self._job_service.get_next_job_run():
                    self.run_job(next_job)
                self._logger.info(f"Sleeping for {self.sleep_time_seconds} seconds...")
                time.sleep(self.sleep_time_seconds)
            except KeyboardInterrupt:
                self._logger.info("Received keyboard interrupt. Exiting...")
                running = False
            except FailedToGetJobRunsError as e:
                self._logger.error(f"Failed to run job and update job status. Maybe the API is down? {e}")
            except Exception as e:
                self._logger.error(f"Unexpected error: {e}")

    def run_job(self, job_run: JobRun) -> None:
        job = self._jobs.get(job_run.job_name)
        if not job:
            self._logger.warning(f"Job {job_run.job_name} not found!")
            self._increment_error_counter_and_update_status(job_run)
            return
        try:
            self._try_set_job_run_status(job_run, status=JobRunStatus.RUNNING.value)
            start_time = time.time()
            self._logger.info(f"Running job {job_run.job_name}...")
            result = job.start(**{arg.name: arg.values for arg in job_run.arguments})
            execution_time = (time.time() - start_time) / 60
            self._logger.info(
                f"Job {job_run.job_name} finished with status {result.exit_status}. Took {execution_time:2f} mins.")

            if result.exit_status == JobExitStatus.SUCCESS:
                self._try_set_job_run_status(job_run, status=JobRunStatus.COMPLETED.value)
            else:
                self._try_set_job_run_status(
                    job_run, status=JobRunStatus.FAILED.value, error_message=result.error_message)
        except Exception as e:
            self._logger.error(f"Failed to run job {job_run.job_name}: {e}")
            if not self._try_set_job_run_status(job_run, status=JobRunStatus.FAILED.value, error_message=str(e)):
                raise

    def _increment_error_counter_and_update_status(self, job_run: JobRun) -> None:
        self._job_lookup_errors[job_run.id] += 1
        if self._job_lookup_errors[job_run.id] > self.job_run_lookup_max_retries:
            self._logger.error(
                f"Job run {job_run.job_name} failed to start {self.job_run_lookup_max_retries} times. Aborting...")
            self._try_set_job_run_status(
                job_run, status=JobRunStatus.FAILED.value, error_message="Failed to start job.")
            self._job_lookup_errors.pop(job_run.id)
        else:
            self._logger.warning(
                f"Job run {job_run.id} ({job_run.job_name}) failed to start after {self._job_lookup_errors[job_run.id]}"
                f" retries.")

    def _try_set_job_run_status(
            self,
            job_run_dto: JobRun,
            status: str,
            error_message: str | None = None) -> bool:
        try:
            self._job_service.update_job_run_status(job_run_dto=job_run_dto, status=status, error_message=error_message)
            return True
        except UpdateFailedError as e:
            self._logger.error(f"Failed to update job run status. Maybe it was grabbed by another instance: {e}")
            return False
