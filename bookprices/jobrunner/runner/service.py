import logging

from requests import HTTPError

from bookprices.shared.api.job import JobApiClient, Endpoint
from bookprices.shared.service.job_service import JobService, FailedToGetJobRunsError


class JobRunnerJobService(JobService):

    def __init__(self, api_client: JobApiClient):
        super().__init__(api_client)
        self._logger = logging.getLogger(__name__)

    def get_next_job_run(self) -> dict:
        try:
            job_run_json = self._job_api_client.get(Endpoint.JOB_RUNS.value)
        except HTTPError as e:
            self._logger.error(f"Failed to get job runs: {e}")
            raise FailedToGetJobRunsError

        return job_run_json