import logging

from bookprices.shared.event.base import Listener
from bookprices.shared.service.job_service import JobService, JobRunPriority, CreationFailedError


class StartJobListener(Listener):
    def __init__(self, job_service: JobService, job_name: str) -> None:
        self._job_service = job_service
        self._job_name = job_name
        self._logger = logging.getLogger(self.__class__.__name__)

    def notify(self, *args, **kwargs) -> None:
        try:
            job_list = self._job_service.get_job_list()
            if not (job :=  next((j for j in job_list if j["name"] == self._job_name), None)):
                return
            self._logger.info(f"Creating job run for {self._job_name}...")
            self._job_service.create_job_run(job, JobRunPriority.HIGH.value)
        except CreationFailedError as ex:
            self._logger.error(f"Error while creating job run for {self._job_name}: {ex}")
