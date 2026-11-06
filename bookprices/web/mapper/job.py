from datetime import datetime
from enum import Enum, StrEnum
from typing import Self

from flask import url_for

from bookprices.shared.service.job_service import (
    JobRunStatus,
    JobRunSchemaFields,
    JobRunArgumentSchemaFields,
    JobSchemaFields)
from bookprices.shared.service.job_run_argument_parser import JobRunArgumentParser
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.job import JobListItem, JobListViewModel, CreateJobViewModel
from bookprices.web.viewmodels.job_run import (
    JobRunListItem,
    JobRunListViewModel,
    JobRunEditViewModel,
    JobRunPriority,
    JobRunCreateViewModel)

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"
JOB_RUN_PRIORITY_TRANSLATIONS = {
    JobRunPriority.LOW: "Lav",
    JobRunPriority.NORMAL: "Normal",
    JobRunPriority.HIGH: "Høj",
}


class JobStatusColor(Enum):
    COMPLETED = "success"
    FAILED = "danger"
    PENDING = "warning"
    RUNNING = "info"
    DEFAULT = "dark"

    @classmethod
    def parse_str(cls, value: str) -> Self | None:
        try:
            return getattr(cls, value.upper())
        except AttributeError:
            return None


class ColumnName(StrEnum):
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    LAST_RUN_AT = "last_run_at"
    IS_ACTIVE = "is_active"
    RUNS_WITH_ARGUMENTS = "runs_with_arguments"
    STATUS = "status"
    PRIORITY = "priority"
    UPDATED = "updated"
    CREATED = "created"
    TIME_ELAPSED = "elapsed"


def map_job_list(jobs_json: dict, job_run_by_job_id: dict[str, dict]) -> JobListViewModel:
    job_list_items = []
    for job in jobs_json:
        last_run_at, last_run_at_status = "-", "-"
        if ((job_run := job_run_by_job_id.get(job[JobSchemaFields.ID]))
                and (last_run_at := job_run.get(JobRunSchemaFields.UPDATED))):
            last_run_at = datetime.fromisoformat(last_run_at).strftime(DATE_FORMAT)
            last_run_at_status = job_run[JobRunSchemaFields.STATUS]

        last_run_at_color = status_color.value \
            if (status_color := JobStatusColor.parse_str(last_run_at_status)) else JobStatusColor.DEFAULT.value
        job_list_items.append(JobListItem(
            id=job[JobSchemaFields.ID],
            name=job[JobSchemaFields.NAME],
            is_active=job[JobSchemaFields.IS_ACTIVE],
            runs_with_arguments=job[JobSchemaFields.RUNS_WITH_ARGUMENTS],
            url=url_for("job.edit", job_id=job[JobSchemaFields.ID]),
            last_run_at=last_run_at,
            last_run_at_color=last_run_at_color))

    translations = {
        ColumnName.NAME.value: "Navn"
    }

    return JobListViewModel(jobs=job_list_items, columns=list(translations.keys()), translations=translations)


def map_job_edit_view_model(job_json: dict) -> CreateJobViewModel:
    return CreateJobViewModel(
        name=job_json[JobSchemaFields.NAME],
        description=job_json[JobSchemaFields.DESCRIPTION],
        active=job_json[JobSchemaFields.IS_ACTIVE],
        id=job_json[JobSchemaFields.ID],
        version=job_json[JobSchemaFields.VERSION],
        runs_with_arguments=job_json[JobSchemaFields.RUNS_WITH_ARGUMENTS],
        form_action_url=url_for(Endpoint.JOB_EDIT.value, job_id=job_json[JobSchemaFields.ID]))


def map_job_run_create_view_model(job: dict) -> JobRunCreateViewModel:
    return JobRunCreateViewModel(
        job_id=job[JobSchemaFields.ID],
        runs_with_arguments=job[JobSchemaFields.RUNS_WITH_ARGUMENTS],
        form_action_url=url_for(Endpoint.JOB_CREATE_JOB_RUN.value),
        priorities=_get_job_run_priorities(),
        translations=JOB_RUN_PRIORITY_TRANSLATIONS)


def map_job_run_edit_view_model(job_run_json: dict) -> JobRunEditViewModel:
    job_run_argument_parser = JobRunArgumentParser()
    arguments = [
        (arg[JobRunArgumentSchemaFields.NAME],
         arg[JobRunArgumentSchemaFields.TYPE],
         arg[JobRunArgumentSchemaFields.VALUES]) for arg in job_run_json[JobRunSchemaFields.ARGUMENTS]]

    arguments_edit_string = job_run_argument_parser.create_arguments_str(arguments)
    editable = job_run_json[JobRunSchemaFields.STATUS] == JobRunStatus.PENDING.value
    return JobRunEditViewModel(
        id=job_run_json[JobRunSchemaFields.ID],
        job_id=job_run_json[JobRunSchemaFields.JOB_ID],
        can_edit=editable,
        status=job_run_json[JobRunSchemaFields.STATUS],
        arguments=arguments_edit_string,
        priority=job_run_json[JobRunSchemaFields.PRIORITY],
        created=datetime.fromisoformat(job_run_json[JobRunSchemaFields.CREATED]).strftime(DATE_FORMAT),
        updated=datetime.fromisoformat(job_run_json[JobRunSchemaFields.UPDATED]).strftime(DATE_FORMAT),
        version=job_run_json[JobRunSchemaFields.VERSION],
        form_action_url=url_for(Endpoint.JOB_UPDATE_JOB_RUN.value, job_run_id=job_run_json[JobRunSchemaFields.ID]),
        error_message=job_run_json[JobRunSchemaFields.ERROR_MESSAGE],
        priorities=_get_job_run_priorities(),
        translations=JOB_RUN_PRIORITY_TRANSLATIONS)


def map_job_run_list(job_runs: dict) -> JobRunListViewModel:
    job_run_list_items = []
    for job_run in job_runs:
        status_value = job_run[JobRunSchemaFields.STATUS]
        status_color = status if (status := JobStatusColor.parse_str(status_value)) else JobStatusColor.DEFAULT
        priority = job_run[JobRunSchemaFields.PRIORITY]

        updated = datetime.fromisoformat(job_run[JobRunSchemaFields.UPDATED])
        created = datetime.fromisoformat(job_run[JobRunSchemaFields.CREATED])
        updated_formatted = updated.strftime(DATE_FORMAT)
        created_formatted = created.strftime(DATE_FORMAT)

        elapsed_formatted = (_format_time_elapsed(created, updated)
            if status_value in {JobRunStatus.COMPLETED, JobRunStatus.FAILED}
            else _format_time_elapsed(created, datetime.now()))

        job_run_list_items.append(JobRunListItem(
            id=job_run[JobRunSchemaFields.ID],
            status=status_value,
            priority=JOB_RUN_PRIORITY_TRANSLATIONS[priority],
            updated=updated_formatted,
            created=created_formatted,
            elapsed=elapsed_formatted,
            status_color=str(status_color.value)))
        
    translations = {
        ColumnName.CREATED: "Oprettet",
        ColumnName.UPDATED: "Opdateret",
        ColumnName.TIME_ELAPSED: "Køretid",
        ColumnName.PRIORITY: "Prioritet",
    }

    return JobRunListViewModel(
        job_runs=job_run_list_items,
        columns=list(translations.keys()),
        translations=translations)


def _format_time_elapsed(time_created: datetime, time_updated: datetime) -> str:
    time_elapsed = time_updated - time_created
    total_seconds = int(time_elapsed.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

def _get_job_run_priorities() -> list[str]:
    return [priority.value for priority in JobRunPriority]
