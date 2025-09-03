import dataclasses
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar

from flask import url_for

from bookprices.web.shared.enum import Endpoint
from bookprices.web.validation.error_message import min_length_not_met, max_length_exceeded
from bookprices.web.validation.input import length_equals_or_longer_than, length_equals_or_shorter_than, \
    is_int_larger_than


@dataclass(frozen=True)
class BookListItemViewModel:
    selected: bool
    id: int
    item_count: int
    name: str
    created: str
    updated: str
    url: str
    edit_url: str
    description: str | None


@dataclass(frozen=True)
class BookListIndexViewModel:
    create_url: str
    booklists: list[BookListItemViewModel]


@dataclass(frozen=True)
class BookListDetailsViewModel:
    id: int
    books: list
    return_url: str
    edit_url: str
    name: str
    created: str
    updated: str
    description: str | None
    booklist_active: bool
    current_page: int
    next_page_url: str | None
    previous_page_url: str | None


@dataclass(frozen=True)
class BookListEditViewModel:
    name_field_name: ClassVar[str] = "name"
    description_field_name: ClassVar[str] = "description"

    name_min_length: ClassVar[int] = 1
    name_max_length: ClassVar[int] = 255
    description_min_length: ClassVar[int] = 1
    description_max_length: ClassVar[int] = 512

    name: str
    description: str | None
    form_action_url: str
    return_url: str
    errors: dict[str, list[str]] = dataclasses.field(default_factory=lambda: defaultdict(list))

    def add_error(self, field_name: str, message: str) -> None:
        self.errors[field_name].append(message)

    def is_valid(self) -> bool:
        if not self.errors:
            self._validate_input()

        return not self.errors

    def _validate_input(self):
        if not length_equals_or_longer_than(self.name, self.name_min_length):
            self.errors[self.name_field_name].append(
                min_length_not_met("Navn", self.name_min_length))
        elif not length_equals_or_shorter_than(self.name, self.name_max_length):
            self.errors[self.name_field_name].append(
                max_length_exceeded("Navn", self.name_max_length))

        if not length_equals_or_longer_than(self.name, self.name_min_length, allow_none=True):
            self.errors[self.description_field_name].append(
                min_length_not_met("Beskrivelse", self.name_min_length))
        elif not length_equals_or_shorter_than(self.name, self.name_max_length, allow_none=True):
            self.errors[self.description_field_name].append(
                max_length_exceeded("Beskrivelse", self.name_max_length))



    @staticmethod
    def empty(form_action_url: str, return_url: str) -> "BookListEditViewModel":
        return BookListEditViewModel(name="", description=None,  form_action_url=form_action_url, return_url=return_url)


@dataclass(frozen=True)
class AddToListRequest:
    book_id_field_name: ClassVar[str] = "book_id"
    book_id: int

    def is_valid(self) -> bool:
        return is_int_larger_than(self.book_id, 0)


@dataclass(frozen=True)
class RemoveFromListRequest:
    book_id_field_name: ClassVar[str] = "book_id"
    book_id: int

    def is_valid(self) -> bool:
        return is_int_larger_than(self.book_id, 0)
