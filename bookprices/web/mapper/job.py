from datetime import datetime
from enum import Enum
from typing import Self

from flask import url_for

from bookprices.web.viewmodels.job import JobListItem, JobListViewModel, CreateJobViewModel
from bookprices.web.viewmodels.job_run import JobRunListItem, JobRunListViewModel, JobRunEditViewModel, JobRunArgument

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


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


class ColumnName(Enum):
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    LAST_RUN_AT = "last_run_at"
    IS_ACTIVE = "is_active"
    STATUS = "status"
    PRIORITY = "priority"
    UPDATED = "updated"
    CREATED = "created"


def map_job_list(jobs_json: dict, job_run_by_job_id: dict[str, dict]) -> JobListViewModel:
    job_list_items = []
    for job in jobs_json:
        last_run_at, last_run_at_status = "-", "-"
        if (job_run := job_run_by_job_id.get(job["id"])) and (last_run_at := job_run.get("updated")):
            last_run_at = datetime.fromisoformat(last_run_at).strftime(DATE_FORMAT)
            last_run_at_status = job_run["status"]

        last_run_at_color = status_color.value \
            if (status_color := JobStatusColor.parse_str(last_run_at_status)) else JobStatusColor.DEFAULT.value
        job_list_items.append(JobListItem(
            id=job["id"],
            name=job["name"],
            description=job["description"],
            is_active=job["isActive"],
            url=url_for("job.edit", job_id=job["id"]),
            last_run_at=last_run_at,
            last_run_at_color=last_run_at_color))

    translations = {
        ColumnName.NAME.value: "Navn",
        ColumnName.DESCRIPTION.value: "Beskrivelse",
        ColumnName.IS_ACTIVE.value: "Aktiv"
    }

    return JobListViewModel(jobs=job_list_items, columns=list(translations.keys()), translations=translations)


def map_job_edit_view_model(job_json: dict) -> CreateJobViewModel:
    return CreateJobViewModel(
        name=job_json["name"],
        description=job_json["description"],
        active=job_json["isActive"],
        id=job_json["id"],
        form_action_url=f"/job/edit/{job_json['id']}")


def map_job_run_edit_view_model(job_run_json: dict) -> JobRunEditViewModel:
    return JobRunEditViewModel(
        id=job_run_json["id"],
        job_id=job_run_json["jobId"],
        status=job_run_json["status"],
        priority=job_run_json["priority"],
        created=datetime.fromisoformat(job_run_json["created"]).strftime(DATE_FORMAT),
        updated=datetime.fromisoformat(job_run_json["updated"]).strftime(DATE_FORMAT),
        arguments=[JobRunArgument(name=arg["name"], type=arg["type"], values=arg["values"])
                   for arg in job_run_json["arguments"]])


def map_job_run_list(job_runs: dict) -> JobRunListViewModel:
    job_run_list_items = []
    for job_run in job_runs:
        status_color = status if (status := JobStatusColor.parse_str(job_run["status"])) else JobStatusColor.DEFAULT
        updated = datetime.fromisoformat(job_run["updated"]).strftime(DATE_FORMAT)
        created = datetime.fromisoformat(job_run["created"]).strftime(DATE_FORMAT)
        job_run_list_items.append(JobRunListItem(
            id=job_run["id"],
            status=job_run["status"],
            priority=job_run["priority"],
            updated=updated,
            created=created,
            status_color=str(status_color.value)))
        
    translations = {
        ColumnName.ID.value: "Id",
        ColumnName.PRIORITY.value: "Prioritet",
        ColumnName.UPDATED.value: "Opdateret",
        ColumnName.CREATED.value: "Oprettet"
    }

    return JobRunListViewModel(job_runs=job_run_list_items, columns=list(translations.keys()), translations=translations)
