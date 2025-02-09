import logging
from dataclasses import dataclass

from requests import HTTPError

from bookprices.shared.api.job import JobApiClient, Endpoint, UrlParameter
from bookprices.shared.service.job_service import (
    JobService, FailedToGetJobRunsError, JobRunSchemaFields, JobRunArgumentSchemaFields, JobRunArgumentType,
    UpdateFailedError, JobRunStatus)


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
    error_message: str | None = None


class RunnerJobService(JobService):

    def __init__(self, api_client: JobApiClient):
        super().__init__(api_client)
        self._logger = logging.getLogger(__name__)

    def get_next_job_run(self) -> JobRun | None:
        try:
            url = (f"{Endpoint.JOB_RUNS.value}?"
                   f"{UrlParameter.STATUS}={JobRunStatus.PENDING.value}&"
                   f"{UrlParameter.LIMIT.value}=1")
            if job_run_json := self._job_api_client.get(url):
                return self._map_json_to_dto(job_run_json[0])

            return None
        except HTTPError as e:
            self._logger.error(f"Failed to get job runs: {e}")
            raise FailedToGetJobRunsError

    def update_job_run_status(
            self,
            job_run_id: str,
            job_id: str,
            status: str,
            error_message: str | None = None) -> None:
        try:
            data = {
                JobRunSchemaFields.JOB_RUN_ID.value: job_run_id,
                JobRunSchemaFields.JOB_ID.value: job_id,
                JobRunSchemaFields.STATUS.value: status}
            if error_message:
                data[JobRunSchemaFields.ERROR_MESSAGE.value] = error_message

            self._job_api_client.patch(Endpoint.get_job_run_url(job_run_id), data=data)
        except HTTPError as e:
            self._logger.error(f"Failed to update job run status: {e}")
            raise UpdateFailedError

    def _map_json_to_dto(self, job_run_json: dict) -> JobRun:
        return JobRun(
            id=job_run_json[JobRunSchemaFields.ID.value],
            job_id=job_run_json[JobRunSchemaFields.JOB_ID.value],
            job_name=job_run_json[JobRunSchemaFields.JOB_NAME.value],
            priority=job_run_json[JobRunSchemaFields.PRIORITY.value],
            status=job_run_json[JobRunSchemaFields.STATUS.value],
            arguments=self._map_job_run_arguments_to_dto(job_run_json[JobRunSchemaFields.ARGUMENTS.value]),
            updated=job_run_json[JobRunSchemaFields.UPDATED.value],
            created=job_run_json[JobRunSchemaFields.CREATED.value],
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



