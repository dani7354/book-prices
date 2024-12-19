from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar

from bookprices.web.shared.input_validation_message import min_length_not_met, max_length_exceeded


@dataclass(frozen=True)
class JobListItem:
    id: str
    name: str
    description: str
    last_run_at: str
    last_run_at_color: str
    url: str
    is_active: bool


@dataclass(frozen=True)
class JobListViewModel:
    columns: list[str]
    translations: dict[str, str]
    jobs: list[JobListItem]


@dataclass(frozen=True)
class CreateJobViewModel:
    name_field_name: ClassVar[str] = "name"
    description_field_name: ClassVar[str] = "description"
    active_field_name: ClassVar[str] = "active"
    id_field_name: ClassVar[str] = "job-id"

    name_min_length: ClassVar[int] = 3
    name_max_length: ClassVar[int] = 256
    description_min_length: ClassVar[int] = 3
    description_max_length: ClassVar[int] = 256

    name: str
    description: str
    active: bool
    form_action_url: str
    id: str | None = None
    errors: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))


    def is_valid(self):
        if not self.errors:
            self._validate_input()

        return not self.errors

    def add_error(self, field_name: str, message: str) -> None:
        self.errors[field_name].append(message)

    def _validate_input(self):
        if len(self.name.strip()) < self.name_min_length:
            self.errors[self.name_field_name].append(min_length_not_met("Navnet", self.name_min_length))
        if len(self.name.strip()) > self.name_max_length:
            self.errors[self.name_field_name].append(max_length_exceeded("Navnet", self.name_max_length))
        if len(self.description.strip()) < self.description_min_length:
            self.errors[self.description_field_name].append(
                min_length_not_met("Beskrivelsen", self.description_min_length))
        if len(self.description.strip()) > self.description_max_length:
            self.errors[self.description_field_name].append(
                max_length_exceeded("Beskrivelsen", self.description_max_length))

    @staticmethod
    def empty(form_action_url: str) -> "CreateJobViewModel":
        return CreateJobViewModel(name="", description="", active=False, form_action_url=form_action_url)
