from bookprices.shared.api.job import JobApiClient, Endpoint
from bookprices.web.mapper.job import map_job_list
from bookprices.web.viewmodels.job import JobListItem


class JobService:

    def __init__(self, job_api_client: JobApiClient) -> None:
        self._job_api_client = job_api_client

    def get_job_list(self) -> dict:
        jobs_json = self._job_api_client.get(Endpoint.JOBS.value)

        return jobs_json

