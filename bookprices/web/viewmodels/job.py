from dataclasses import dataclass


@dataclass(frozen=True)
class JobListItem:
    id: str
    name: str
    description: str
    is_active: bool


@dataclass(frozen=True)
class JobListViewModel:
    columns: list[str]
    translations: dict[str, str]
    jobs: list[JobListItem]