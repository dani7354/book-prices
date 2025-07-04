from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar, Optional

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.validation.error_message import min_length_not_met, max_length_exceeded


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
    edit_current_user: bool
    access_level: str
    form_action_url: str
    return_url: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    image_url: Optional[str] = None
    access_levels: list[UserAccessLevel] = field(default_factory=lambda: list(UserAccessLevel))
    input_errors: dict[str, list[str]] = field(init=False, default_factory=lambda: defaultdict(list))

    def validate_input(self) -> None:
        self.input_errors.clear()
        if len(self.email) < self.email_min_length:
            self.add_input_error(self.email_field_name, min_length_not_met("Email", self.email_min_length))
        if len(self.email) > self.email_max_length:
            self.add_input_error(self.email_field_name, max_length_exceeded("Email", self.email_max_length))
        if len(self.firstname) < self.firstname_min_length:
            self.add_input_error(self.firstname_field_name, min_length_not_met("Fornavn", self.firstname_min_length))
        if len(self.firstname) > self.firstname_max_length:
            self.add_input_error(self.firstname_field_name, max_length_exceeded("Fornavn", self.firstname_max_length))
        if self.lastname and len(self.lastname) < self.lastname_min_length:
            self.add_input_error(self.lastname_field_name, min_length_not_met("Efternavn", self.lastname_min_length))
        if self.lastname and len(self.lastname) > self.lastname_max_length:
            self.add_input_error(
                self.lastname_field_name, max_length_exceeded("Efternavn", self.lastname_max_length))
        if not UserAccessLevel.from_string(self.access_level):
            self.add_input_error(self.access_level_field_name, "Adgangsniveau ugyldigt!")

    def add_input_error(self, field_name:str, error_message: str) -> None:
        self.input_errors[field_name].append(error_message)

    def is_valid(self) -> bool:
        self.validate_input()
        return not self.input_errors


@dataclass(frozen=True)
class UserListItemViewModel:
    id: str
    email: str
    firstname: str
    lastname: str
    is_active: bool
    access_level: str
    edit_url: str
    created: Optional[str] = None
    updated: Optional[str] = None


@dataclass(frozen=True)
class UserListViewModel:
    can_edit: bool
    can_delete: bool
    current_page: int
    next_page_url: str
    previous_page_url: str
    users: list[UserListItemViewModel]
