import logging

from bookprices.job.service.argument_service import JobRunArgumentService, JobRunArgumentName
from bookprices.shared.event.base import Listener
from bookprices.shared.service.job_service import JobService, JobRunPriority, CreationFailedError


class StartJobListener(Listener):
    def __init__(self, job_service: JobService, job_run_argument_service: JobRunArgumentService, job_name: str) -> None:
        self._job_service = job_service
        self._job_run_argument_service = job_run_argument_service
        self._job_name = job_name
        self._logger = logging.getLogger(self.__class__.__name__)

    def notify(self, *args, **kwargs) -> None:
        try:
            job_list = self._job_service.get_job_list()
            if not (job :=  next((j for j in job_list if j["name"] == self._job_name), None)):
                return

            self._logger.info(f"Creating job run for {self._job_name}...")

            if kwargs:
                arguments = self._job_run_argument_service.create_job_run_payload(
                    kwargs,
                    argument_names=[JobRunArgumentName.BOOK_IDS])
            else:
                arguments = []

            self._job_service.create_job_run(job_id=job["id"], priority=JobRunPriority.HIGH.value, arguments=arguments)
        except CreationFailedError as ex:
            self._logger.error(f"Error while creating job run for {self._job_name}: {ex}")
