import logging
from dataclasses import dataclass

from requests import HTTPError

from bookprices.shared.api.error import ApiUnavailableError
from bookprices.shared.api.job import JobApiClient, Endpoint, UrlParameter
from bookprices.shared.service.job_service import (
    FailedToGetJobRunsError, JobRunSchemaFields, JobRunArgumentSchemaFields, JobRunArgumentType, UpdateFailedError,
    JobRunStatus, JobSourceUnavailableError)


@dataclass(frozen=True)
class JobRunArgument:
    name: str
    type: str
    values: list[str] | list[int] | list[bool]


@dataclass(frozen=True)
class JobRun:
    id: str
    job_id: str
    job_name: str
    priority: str
    status: str
    arguments: list[JobRunArgument]
    updated: str
    created: str
    version: str
    error_message: str | None = None


class RunnerJobService:
    """ Job service for the job runner """

    def __init__(self, job_api_client: JobApiClient) -> None:
        self._job_api_client = job_api_client
        self._logger = logging.getLogger(__name__)

    def get_next_job_run_dto(self) -> JobRun | None:
        next_job_id = None
        try:
            if not (next_job_id := self._get_next_job_run_id_from_list()):
                return None
            self._logger.debug(f"Got next job run with id {next_job_id}")
            job_run_dto = self.get_job_run_dto(next_job_id)

            return job_run_dto
        except ApiUnavailableError as e:
            self._logger.error(f"Failed to get next job run with id {next_job_id}")
            raise JobSourceUnavailableError from e
        except HTTPError as e:
            self._logger.error(f"Failed to get job runs: {e}")
            raise FailedToGetJobRunsError

    def get_job_run_dto(self, job_run_id: str) -> JobRun | None:
        try:
            if not (job_run_json := self._job_api_client.get(Endpoint.get_job_run_url(job_run_id))):
                return None
            job_run_dto = self._map_job_run_json_to_dto(job_run_json)

            return job_run_dto
        except HTTPError as e:
            self._logger.error(f"Failed to get job run with id {job_run_id}: {e}")
            return None

    def update_job_run_status(
            self,
            job_run_dto: JobRun,
            status: str,
            error_message: str | None = None) -> None:
        try:
            data = {
                JobRunSchemaFields.JOB_RUN_ID.value: job_run_dto.id,
                JobRunSchemaFields.JOB_ID.value: job_run_dto.job_id,
                JobRunSchemaFields.VERSION.value: job_run_dto.version,
                JobRunSchemaFields.STATUS.value: status}
            if error_message:
                data[JobRunSchemaFields.ERROR_MESSAGE.value] = error_message
            self._logger.debug(f"Updating job run with id {job_run_dto.id} to status {status}")
            self._job_api_client.patch(Endpoint.get_job_run_url(job_run_dto.id), data=data)
        except ApiUnavailableError as e:
            self._logger.error(f"Failed to update job run status for job run with id {job_run_dto.id}")
            raise JobSourceUnavailableError from e
        except HTTPError as e:
            self._logger.error(f"Failed to update job run status: {e}")
            raise UpdateFailedError

    def _get_next_job_run_id_from_list(self) -> str | None:
        try:
            url = (f"{Endpoint.JOB_RUNS.value}?"
                   f"{UrlParameter.STATUS.value}={JobRunStatus.PENDING.value}&"
                   f"{UrlParameter.SORT_BY.value}=Priority&"
                   f"{UrlParameter.SORT_DIRECTION.value}=Descending&"
                   f"{UrlParameter.LIMIT.value}=1")

            job_run_json = self._job_api_client.get(url)
            if job_run_json:
                return job_run_json[0][JobRunSchemaFields.ID.value]
            return None
        except ApiUnavailableError as e:
            self._logger.error("Failed to get next job run id. Job API is unavailable")
            raise JobSourceUnavailableError from e
        except HTTPError as e:
            self._logger.error(f"Failed to get job runs: {e}")
            raise FailedToGetJobRunsError

    def _map_job_run_json_to_dto(self, job_run_json: dict) -> JobRun:
        self._logger.info(job_run_json)
        return JobRun(
            id=job_run_json[JobRunSchemaFields.ID.value],
            job_id=job_run_json[JobRunSchemaFields.JOB_ID.value],
            job_name=job_run_json[JobRunSchemaFields.JOB_NAME.value],
            priority=job_run_json[JobRunSchemaFields.PRIORITY.value],
            status=job_run_json[JobRunSchemaFields.STATUS.value],
            arguments=[],  # self._map_job_run_arguments_to_dto(job_run_json[JobRunSchemaFields.ARGUMENTS.value]),
            updated=job_run_json[JobRunSchemaFields.UPDATED.value],
            created=job_run_json[JobRunSchemaFields.CREATED.value],
            version=job_run_json[JobRunSchemaFields.VERSION.value],
            error_message=job_run_json.get(JobRunSchemaFields.ERROR_MESSAGE.value))

    def _map_job_run_arguments_to_dto(self, arguments_response: list[dict]) -> list[JobRunArgument]:
        arguments = []
        for arg in arguments_response:
            name = arg[JobRunArgumentSchemaFields.NAME.value]
            arg_type = arg[JobRunArgumentSchemaFields.TYPE.value]
            try:
                if arg_type == JobRunArgumentType.STRING.value:
                    values = arg[JobRunArgumentSchemaFields.VALUES.value]
                elif arg_type == JobRunArgumentType.INTEGER.value:
                    values = [int(value) for value in arg[JobRunArgumentSchemaFields.VALUES.value]]
                elif arg_type == JobRunArgumentType.BOOLEAN.value:
                    values = [bool(value) for value in arg[JobRunArgumentSchemaFields.VALUES.value]]
                else:
                    self._logger.warning(f"Unknown argument type: {arg_type}")
                    continue
                arguments.append(JobRunArgument(name, arg_type, values))
            except (KeyError, TypeError, ValueError) as e:
                self._logger.error(f"Failed to map job run arguments {name} with type {arg_type}: {e}")
                continue
        return arguments
