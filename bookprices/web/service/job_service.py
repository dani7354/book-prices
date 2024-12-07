import logging

from bookprices.shared.api.job import JobApiClient, Endpoint
from bookprices.web.mapper.job import map_job_list
from bookprices.web.viewmodels.job import JobListItem


logger = logging.getLogger(__name__)


class JobAlreadyExistError(Exception):
    pass


class JobService:

    def __init__(self, job_api_client: JobApiClient) -> None:
        self._job_api_client = job_api_client

    def get_job_list(self) -> dict:
        jobs_json = self._job_api_client.get(Endpoint.JOBS.value)

        return jobs_json

    def create_job(self, name: str, description: str, is_active: bool) -> None:
        job_list_json = self._job_api_client.get(Endpoint.JOBS.value)
        if any(job["name"] == name for job in job_list_json):
            error_msg = f"Job with name {name} already exist."
            logger.error(error_msg)
            raise JobAlreadyExistError(error_msg)

        self._job_api_client.post(
            Endpoint.JOBS.value,
            json={"Name": name, "Description": description, "IsActive": is_active})
