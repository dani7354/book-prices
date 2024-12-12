from datetime import datetime
from enum import Enum
from typing import Self

from flask import url_for

from bookprices.web.viewmodels.job import JobListItem, JobListViewModel, CreateJobViewModel


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


def map_job_list(jobs_json: dict, job_run_by_job_id: dict[str, dict]) -> JobListViewModel:
    job_list_items = []
    for job in jobs_json:
        last_run_at, last_run_at_status = "-", "-"
        if (job_run := job_run_by_job_id.get(job["id"])) and (last_run_at := job_run.get("updated")):
            last_run_at = datetime.fromisoformat(last_run_at).strftime("%d-%m-%Y %H:%M:%S")
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
        form_action_url=f"/job/edit/{job_json['id']}")
