import logging
from enum import Enum
from requests.exceptions import HTTPError

from bookprices.shared.api.error import ApiUnavailableError
from bookprices.shared.api.job import JobApiClient, Endpoint, UrlParameter

logger = logging.getLogger(__name__)


class AlreadyExistError(Exception):
    pass


class DeletionFailedError(Exception):
    pass


class CreationFailedError(Exception):
    pass


class UpdateFailedError(Exception):
    pass


class FailedToGetJobRunsError(Exception):
    pass


class SourceUnavailableError(Exception):
    pass


class JobSchemaFields(Enum):
    ID = "id"
    JOB_ID = "jobId"
    NAME = "name"
    DESCRIPTION = "description"
    IS_ACTIVE = "isActive"
    VERSION = "version"


class JobRunSchemaFields(Enum):
    ID = "id"
    JOB_NAME = "jobName"
    JOB_RUN_ID = "jobRunId"
    JOB_ID = "jobId"
    PRIORITY = "priority"
    STATUS = "status"
    UPDATED = "updated"
    CREATED = "created"
    ERROR_MESSAGE = "errorMessage"
    ARGUMENTS = "arguments"
    VERSION = "version"


class JobRunArgumentSchemaFields(Enum):
    NAME = "name"
    TYPE = "type"
    VALUES = "values"


class JobRunArgumentType(Enum):
    STRING = "str"
    INTEGER = "int"
    BOOLEAN = "bool"


class JobRunStatus(Enum):
    COMPLETED = "Completed"
    FAILED = "Failed"
    PENDING = "Pending"
    RUNNING = "Running"


class JobRunPriority(Enum):
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"


class JobService:

    def __init__(self, job_api_client: JobApiClient) -> None:
        self._job_api_client = job_api_client

    def get_job_list(self) -> dict:
        try:
            jobs_json = self._job_api_client.get(Endpoint.JOBS.value)
            return jobs_json
        except ApiUnavailableError as ex:
            raise SourceUnavailableError from ex
        except HTTPError as e:
            logger.error(f"Failed to get job list. Error: {e}")
            return {}

    def get_job(self, job_id: str) -> dict | None:
        try:
            job_json = self._job_api_client.get(Endpoint.get_job_url(job_id))
            return job_json
        except ApiUnavailableError as ex:
            raise SourceUnavailableError from ex
        except HTTPError as ex:
            logger.error(f"Failed to get job with id {job_id}. Error: {ex}")
            return None

    def get_job_run(self, job_run_id: str) -> dict | None:
        try:
            job_run_json = self._job_api_client.get(Endpoint.get_job_run_url(job_run_id))
            return job_run_json
        except ApiUnavailableError as ex:
            raise SourceUnavailableError from ex
        except HTTPError as ex:
            logger.error(f"Failed to get job run with id {job_run_id}. Error: {ex}")
            return None

    def get_job_run_for_jobs(self, job_ids: list[str]) -> dict[str, dict]:
        job_run_count = 1
        job_runs_by_job_id = {}
        for job_id in job_ids:
            try:
                url = (f"{Endpoint.JOB_RUNS.value}"
                       f"?{UrlParameter.JOB_ID.value}={job_id}"
                       f"&{UrlParameter.LIMIT.value}={job_run_count}"
                       f"&{UrlParameter.SORT_BY.value}={JobRunSchemaFields.UPDATED.value}"
                       f"&{UrlParameter.SORT_DIRECTION.value}=Descending")
                if job_run_response := self._job_api_client.get(url):
                    job_runs_by_job_id[job_id], = job_run_response
            except ApiUnavailableError as ex:
                raise SourceUnavailableError from ex
            except HTTPError as ex:
                logger.error(f"Failed to get job runs for job with id {job_id}. Error: {ex}")

        return job_runs_by_job_id

    def get_job_runs(self, job_id: str | None = None) -> dict:
        try:
            max_job_runs_to_load = 50
            url = (f"{Endpoint.JOB_RUNS.value}"
                   f"?{UrlParameter.LIMIT.value}={max_job_runs_to_load}"
                   f"&{UrlParameter.SORT_BY.value}={JobRunSchemaFields.UPDATED.value}"
                   f"&{UrlParameter.SORT_DIRECTION.value}=Descending")
            if job_id:
                url += f"&{UrlParameter.JOB_ID.value}={job_id}"
            job_runs = self._job_api_client.get(url)
            return job_runs
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to get job runs. Error: {ex}")
            raise FailedToGetJobRunsError("Failed to get job runs.")

    def create_job(self, name: str, description: str, is_active: bool) -> None:
        job_list_json = self._job_api_client.get(Endpoint.JOBS.value)
        if any(job["name"] == name for job in job_list_json):
            error_msg = f"Job with name {name} already exist."
            logger.error(error_msg)
            raise AlreadyExistError(error_msg)
        try:
            self._job_api_client.post(
                Endpoint.JOBS.value,
                data={
                    JobSchemaFields.NAME.value: name,
                    JobSchemaFields.DESCRIPTION.value: description,
                    JobSchemaFields.IS_ACTIVE.value: is_active})
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to create job with name {name}. Error: {ex}")
            raise CreationFailedError(f"Job with name {name} could not be created.")

    def create_job_run(self, job_id: str, priority: str) -> None:
        try:
            self._job_api_client.post(
                Endpoint.JOB_RUNS.value,
                data={
                    JobRunSchemaFields.JOB_ID.value: job_id,
                    JobRunSchemaFields.PRIORITY.value: priority})
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to create job run for job with id {job_id}. Error: {ex}")
            raise CreationFailedError(f"Job run for job with id {job_id} could not be created.")

    def update_job(self, job_id: str, name: str, description: str, version: str, is_active: bool) -> None:
        try:
            job_list = self.get_job_list()
            if any(job["name"] == name and job["id"] != job_id for job in job_list):
                error_msg = f"Job with name {name} already exist."
                logger.error(error_msg)
                raise AlreadyExistError(error_msg)

            self._job_api_client.put(
                Endpoint.get_job_url(job_id),
                data={
                    JobSchemaFields.ID.value: job_id,
                    JobSchemaFields.NAME.value: name,
                    JobSchemaFields.DESCRIPTION.value: description,
                    JobSchemaFields.VERSION.value: version,
                    JobSchemaFields.IS_ACTIVE.value: is_active})
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to update job with id {job_id}. Error: {ex}")
            raise UpdateFailedError(f"Job with id {job_id} could not be updated.")

    def update_job_run(self, job_id: str, job_run_id: str, priority: str, version: str) -> None:
        try:
            self._job_api_client.patch(
                Endpoint.get_job_run_url(job_run_id),
                data={
                    JobRunSchemaFields.JOB_RUN_ID.value: job_run_id,
                    JobRunSchemaFields.JOB_ID.value: job_id,
                    JobRunSchemaFields.PRIORITY.value: priority,
                    JobRunSchemaFields.VERSION.value: version})
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to update job run with id {job_run_id}. Error: {ex}")
            raise CreationFailedError(f"Job run with id {job_run_id} could not be updated.")

    def delete_job(self, job_id: str) -> None:
        try:
            self._job_api_client.delete(Endpoint.get_job_url(job_id))
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to delete job with id {job_id}. Error: {ex}")
            raise DeletionFailedError(f"Job with id {job_id} could not be deleted.")

    def delete_job_run(self, job_run_id: str) -> None:
        try:
            self._job_api_client.delete(Endpoint.get_job_run_url(job_run_id))
        except (HTTPError, ApiUnavailableError) as ex:
            logger.error(f"Failed to delete job run with id {job_run_id}. Error: {ex}")
            raise DeletionFailedError(f"Job run with id {job_run_id} could not be deleted.")
