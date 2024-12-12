import logging
from enum import Enum
from urllib.error import HTTPError

from bookprices.shared.api.job import JobApiClient, Endpoint


logger = logging.getLogger(__name__)


class JobAlreadyExistError(Exception):
    pass


class JobDeletionFailedError(Exception):
    pass


class JobCreationFailedError(Exception):
    pass


class JobUpdateFailedError(Exception):
    pass


class SchemaFields(Enum):
    ID = "Id"
    NAME = "Name"
    DESCRIPTION = "Description"
    IS_ACTIVE = "IsActive"


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

    def get_job_run_for_jobs(self, job_ids: [str]) -> dict[str, dict]:
        job_runs_by_job_id = {}
        for job_id in job_ids:
            try:
                url = f"{Endpoint.JOB_RUNS.value}?jobId={job_id}&limit=1"
                if job_run_response := self._job_api_client.get(url):
                    job_runs_by_job_id[job_id], = job_run_response
            except HTTPError as ex:
                logger.error(f"Failed to get job runs for job with id {job_id}. Error: {ex}")

        return job_runs_by_job_id

    def create_job(self, name: str, description: str, is_active: bool) -> None:
        job_list_json = self._job_api_client.get(Endpoint.JOBS.value)
        if any(job["name"] == name for job in job_list_json):
            error_msg = f"Job with name {name} already exist."
            logger.error(error_msg)
            raise JobAlreadyExistError(error_msg)
        try:
            self._job_api_client.post(
                Endpoint.JOBS.value,
                data={
                    SchemaFields.NAME.value: name,
                    SchemaFields.DESCRIPTION.value: description,
                    SchemaFields.IS_ACTIVE.value: is_active})
        except HTTPError as ex:
            logger.error(f"Failed to create job with name {name}. Error: {ex}")
            raise JobCreationFailedError(f"Job with name {name} could not be created.")

    def update_job(self, job_id: str, name: str, description: str, is_active:bool) -> None:
        try:
            job_list = self.get_job_list()
            if any(job["name"] == name and job["id"] != job_id for job in job_list):
                error_msg = f"Job with name {name} already exist."
                logger.error(error_msg)
                raise JobAlreadyExistError(error_msg)

            self._job_api_client.put(
                Endpoint.get_job_url(job_id),
                data={
                    SchemaFields.ID.value: job_id,
                    SchemaFields.NAME.value: name,
                    SchemaFields.DESCRIPTION.value: description,
                    SchemaFields.IS_ACTIVE.value: is_active})
        except HTTPError as ex:
            logger.error(f"Failed to update job with id {job_id}. Error: {ex}")
            raise JobUpdateFailedError(f"Job with id {job_id} could not be updated.")

    def delete_job(self, job_id: str) -> None:
        try:
            self._job_api_client.delete(Endpoint.get_job_url(job_id))
        except HTTPError as ex:
            logger.error(f"Failed to delete job with id {job_id}. Error: {ex}")
            raise JobDeletionFailedError(f"Job with id {job_id} could not be deleted.")
