from dataclasses import dataclass, field
from enum import StrEnum
from typing import ClassVar


class JobRunPriority(StrEnum):
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"

    @classmethod
    def get_values(cls) -> list[str]:
        return [str(x) for x in cls.__members__.values()]


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
    job_id_field_name: ClassVar[str] = "job_id"
    priority_field_name: ClassVar[str] = "priority"

    form_action_url: str
    job_id: str
    priorities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class JobRunEditViewModel:
    job_id_field_name: ClassVar[str] = "job_id"
    priority_field_name: ClassVar[str] = "priority"

    id: str
    job_id: str
    status: str
    priority: str
    created: str
    updated: str
    form_action_url: str
    priorities: dict[str, str] = field(default_factory=dict)
    arguments: list[JobRunArgument] = field(default_factory=list)
