from dataclasses import dataclass


@dataclass(frozen=True)
class JobRunListItem:
    id: str
    created: str
    updated: str
    status: str
    priority: str
    status_color: str


@dataclass(frozen=True)
class JobRunListViewModel:
    columns: list[str]
    translations: dict[str, str]
    job_runs: list[JobRunListItem]
