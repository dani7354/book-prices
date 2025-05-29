from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar, Optional
from bookprices.web.shared.input_validation_message import min_length_not_met, max_length_exceeded


@dataclass(frozen=True)
class UserEditViewModel:
    id_field_name: ClassVar[str] = "id"
    created_field_name: ClassVar[str] = "created"
    updated_field_name: ClassVar[str] = "updated"
    email_field_name: ClassVar[str] = "email"
    firstname_field_name: ClassVar[str] = "firstname"
    lastname_field_name: ClassVar[str] = "lastname"
    is_active_field_name: ClassVar[str] = "is_active"
    access_level_field_name: ClassVar[str] = "access_level"

    email_min_length: ClassVar[int] = 1
    email_max_length: ClassVar[int] = 255
    firstname_min_length: ClassVar[int] = 1
    firstname_max_length: ClassVar[int] = 255
    lastname_min_length: ClassVar[int] = 1
    lastname_max_length: ClassVar[int] = 255

    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    access_level: str
    created: Optional[str] = None
    updated: Optional[str] = None
    image_url: Optional[str] = None
    input_errors: dict[str, list[str]] = field(init=False, default_factory=lambda: defaultdict(list))

    def validate_input(self) -> None:
        self.input_errors.clear()
        if len(self.email) < self.email_min_length:
            self.input_errors[self.email_field_name].append(
                min_length_not_met("Email", self.email_min_length))
        if len(self.email) > self.email_max_length:
            self.input_errors[self.email_field_name].append(
                max_length_exceeded("Email", self.email_max_length))
        if len(self.firstname) < self.firstname_min_length:
            self.input_errors[self.firstname_field_name].append(
                min_length_not_met("Fornavn", self.firstname_min_length))
        if len(self.firstname) > self.firstname_max_length:
            self.input_errors[self.firstname_field_name].append(
                max_length_exceeded("Fornavn", self.firstname_max_length))
        if len(self.lastname) < self.lastname_min_length:
            self.input_errors[self.lastname_field_name].append(
                min_length_not_met("Efternavn", self.lastname_min_length))
        if len(self.lastname) > self.lastname_max_length:
            self.input_errors[self.lastname_field_name].append(
                max_length_exceeded("Efternavn", self.lastname_max_length))

    def is_valid(self) -> bool:
        self.validate_input()
        return not self.input_errors
