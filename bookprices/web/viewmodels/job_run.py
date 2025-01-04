from dataclasses import dataclass, field
from enum import StrEnum


class JobRunPriority(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


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
class JobRunCreateViewModel:
    form_action_url: str
    job_id: str
    priorities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class JobRunEditViewModel:
    id: str
    job_id: str
    status: str
    priority: str
    created: str
    updated: str
    form_action_url: str
    priorities: dict[str, str] = field(default_factory=dict)
    arguments: list[JobRunArgument] = field(default_factory=list)
