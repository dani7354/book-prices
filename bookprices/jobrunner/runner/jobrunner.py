import time
from logging import getLogger
from typing import ClassVar, Sequence

from bookprices.jobrunner.job.base import JobExitStatus, JobBase
from bookprices.jobrunner.runner.service import RunnerJobService, JobRun
from bookprices.shared.config.config import Config
from bookprices.shared.service.job_service import UpdateFailedError, JobRunStatus


class JobRunner:
    sleep_time_seconds: ClassVar[int] = 10

    def __init__(self, config: Config, job: Sequence[JobBase], job_service: RunnerJobService) -> None:
        self._config = config
        self._job_service = job_service
        self._logger = getLogger(__name__)
        self._jobs = {job.name: job for job in job}

    def start(self) -> None:
        self._logger.info("Starting job runner...")
        running = True
        while running:
            try:
                if next_job := self._job_service.get_next_job_run():
                    self.run_job(next_job)
                else:
                    time.sleep(self.sleep_time_seconds)
            except KeyboardInterrupt:
                self._logger.info("Received keyboard interrupt. Exiting...")
                running = False
            except Exception as e:
                self._logger.error(f"Failed to run job and update job status. Maybe the API is down? {e}")

    def run_job(self, job_run: JobRun) -> None:
        job = self._jobs.get(job_run.job_name)
        if not job:
            self._logger.warning(f"Job {job_run.job_name} not found!")
            return
        try:
            self._try_set_job_run_status(job_run.id, job_run.job_id, status=JobRunStatus.RUNNING.value)
            result = job.start(**{arg.name: arg.values for arg in job_run.arguments})
            if result.exit_status == JobExitStatus.SUCCESS:
                self._try_set_job_run_status(job_run.id, job_run.job_id, status=JobRunStatus.COMPLETED.value)
            else:
                self._try_set_job_run_status(
                    job_run.id, job_run.job_id, status=JobRunStatus.FAILED.value, error_message=result.error_message)
        except Exception as e:
            self._logger.error(f"Failed to run job {job_run.job_name}: {e}")
            if not self._try_set_job_run_status(
                    job_run.id, job_run.job_id, status=JobRunStatus.FAILED.value, error_message=str(e)):
                raise from e

    def _try_set_job_run_status(
            self,
            job_run_id: str,
            job_id: str,
            status: str,
            error_message: str | None = None) -> bool:
        try:
            self._job_service.update_job_run_status(job_run_id, job_id, status=status, error_message=error_message)
            return True
        except UpdateFailedError as e:
            self._logger.error(f"Failed to update job run status. Maybe it was grabbed by another instance: {e}")
            return False
