import logging
from urllib.error import HTTPError

from bookprices.shared.api.job import JobApiClient, Endpoint


logger = logging.getLogger(__name__)


class JobAlreadyExistError(Exception):
    pass


class JobDeletionFailedError(Exception):
    pass


class JobCreationFailedError(Exception):
    pass


class JobService:

    def __init__(self, job_api_client: JobApiClient) -> None:
        self._job_api_client = job_api_client

    def get_job_list(self) -> dict:
        jobs_json = self._job_api_client.get(Endpoint.JOBS.value)

        return jobs_json

    def get_job(self, job_id: str) -> dict | None:
        try:
            job_json = self._job_api_client.get(Endpoint.get_job_url(job_id))
            return job_json
        except HTTPError as ex:
            logger.error(f"Failed to get job with id {job_id}. Error: {ex}")
            return None

    def create_job(self, name: str, description: str, is_active: bool) -> None:
        job_list_json = self._job_api_client.get(Endpoint.JOBS.value)
        if any(job["name"] == name for job in job_list_json):
            error_msg = f"Job with name {name} already exist."
            logger.error(error_msg)
            raise JobAlreadyExistError(error_msg)

        try:
            self._job_api_client.post(
                Endpoint.JOBS.value,
                data={"Name": name, "Description": description, "IsActive": is_active})
        except HTTPError as ex:
            logger.error(f"Failed to create job with name {name}. Error: {ex}")
            raise JobCreationFailedError(f"Job with name {name} could not be created.")

    def delete_job(self, job_id: str) -> None:
        try:
            self._job_api_client.delete(Endpoint.get_job_url(job_id))
        except HTTPError as ex:
            logger.error(f"Failed to delete job with id {job_id}. Error: {ex}")
            raise JobDeletionFailedError(f"Job with id {job_id} could not be deleted.")
