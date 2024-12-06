from bookprices.web.viewmodels.job import JobListItem, JobListViewModel


ID_COLUMN_NAME = "id"
NAME_COLUMN_NAME = "name"
DESCRIPTION_COLUMN_NAME = "description"



def map_job_list(jobs_json: dict) -> JobListViewModel:
    job_list_items =  [
        JobListItem(
            id=job["id"],
            name=job["name"],
            description=job["description"],
            is_active=job["isActive"])
        for job in jobs_json]

    translations = {
        NAME_COLUMN_NAME: "Navn",
        DESCRIPTION_COLUMN_NAME: "Beskrivelse"
    }

    return JobListViewModel(jobs=job_list_items, columns=list(translations.keys()), translations=translations)


