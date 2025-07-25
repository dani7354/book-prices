import dataclasses
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar

from flask import url_for

from bookprices.web.shared.enum import Endpoint
from bookprices.web.validation.error_message import min_length_not_met, max_length_exceeded
from bookprices.web.validation.input import length_equals_or_longer_than, length_equals_or_shorter_than


@dataclass(frozen=True)
class BookListItemViewModel:
    id: int
    item_count: int
    name: str
    created: str
    updated: str
    url: str


@dataclass(frozen=True)
class BookListIndexViewModel:
    create_url: str
    booklists: list[BookListItemViewModel]


@dataclass(frozen=True)
class BookListDetailsViewModel:
    books: list
    return_url: str
    name: str
    created: str
    updated: str


@dataclass(frozen=True)
class BookListEditViewModel:
    name_field_name: ClassVar[str] = "name"

    name_min_length: ClassVar[int] = 1
    name_max_length: ClassVar[int] = 255

    name: str
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
                min_length_not_met("Navnet", self.name_min_length))
        elif not length_equals_or_shorter_than(self.name, self.name_max_length):
            self.errors[self.name_field_name].append(
                max_length_exceeded("Navnet", self.name_max_length))

    @staticmethod
    def empty(form_action_url: str, return_url: str) -> "BookListEditViewModel":
        return BookListEditViewModel(name="", form_action_url=form_action_url, return_url=return_url)


@dataclass(frozen=True)
class AddToListRequest:
    book_id_field_name: ClassVar[str] = "book_id"
    booklist_id_field_name: ClassVar[str] = "booklist_id"

    book_id: int
    booklist_id: int
