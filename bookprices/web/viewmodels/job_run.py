from dataclasses import dataclass, field


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


@dataclass(frozen=True)
class JobRunArgument:
    name: str
    type: str
    values: list[str]


@dataclass(frozen=True)
class JobRunEditViewModel:
    id: str
    job_id: str
    status: str
    priority: str
    created: str
    updated: str
    arguments: list[JobRunArgument] = field(default_factory=list)
