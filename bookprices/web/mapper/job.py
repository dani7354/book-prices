from enum import Enum

from flask import url_for

from bookprices.web.viewmodels.job import JobListItem, JobListViewModel, CreateJobViewModel


class ColumnName(Enum):
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    LAST_RUN_AT = "last_run_at"
    IS_ACTIVE = "is_active"


def map_job_list(jobs_json: dict) -> JobListViewModel:
    job_list_items =  [
        JobListItem(
            id=job["id"],
            name=job["name"],
            description=job["description"],
            is_active=job["isActive"],
            url=url_for("job.edit", job_id=job["id"]),
            last_run_at="XX",
            last_run_status="XX")
        for job in jobs_json]

    translations = {
        ColumnName.NAME.value: "Navn",
        ColumnName.DESCRIPTION.value: "Beskrivelse",
        ColumnName.LAST_RUN_AT.value: "Sidste kørsel",
        ColumnName.IS_ACTIVE.value: "Aktiv"
    }

    return JobListViewModel(jobs=job_list_items, columns=list(translations.keys()), translations=translations)


def map_job_edit_view_model(job_json: dict) -> CreateJobViewModel:
    return CreateJobViewModel(
        name=job_json["name"],
        description=job_json["description"],
        active=job_json["isActive"],
        form_action_url=f"/job/edit/{job_json['id']}")


