import dataclasses
from collections import defaultdict
from typing import ClassVar

from bookprices.web.validation.error_message import min_length_not_met, max_length_exceeded
from bookprices.web.validation.input import length_equals_or_longer_than, length_equals_or_shorter_than


@dataclasses.dataclass(frozen=True)
class BookStoreListItem:
    id: int
    name: str
    url: str
    edit_url: str


@dataclasses.dataclass(frozen=True)
class BookStoreListViewModel:
    can_edit: bool
    can_delete: bool
    bookstores: list[BookStoreListItem]


@dataclasses.dataclass(frozen=True)
class BookStoreEditViewModel:
    has_dynamic_content_field_name: ClassVar[str] = "has-dynamic-content"
    id_field_name: ClassVar[str] = "id"
    name_field_name: ClassVar[str] = "name"
    url_field_name: ClassVar[str] = "url"
    search_url_field_name: ClassVar[str] = "search-url"
    search_result_css_field_name: ClassVar[str] = "search-result-css"
    image_css_field_name: ClassVar[str] = "image-css"
    isbn_css_field_name: ClassVar[str] = "isbn-css"
    price_css_field_name: ClassVar[str] = "price-css"
    price_format_field_name: ClassVar[str] = "price-format"

    name_min_length: ClassVar[int] = 1
    name_max_length: ClassVar[int] = 255
    url_min_length: ClassVar[int] = 1
    url_max_length: ClassVar[int] = 255
    search_url_min_length: ClassVar[int] = 1
    search_url_max_length: ClassVar[int] = 255
    search_result_css_min_length: ClassVar[int] = 1
    search_result_css_max_length: ClassVar[int] = 255
    price_css_min_length: ClassVar[int] = 1
    price_css_max_length: ClassVar[int] = 255
    image_css_min_length : ClassVar[int] = 1
    image_css_max_length: ClassVar[int] = 255
    isbn_css_min_length: ClassVar[int] = 1
    isbn_css_max_length: ClassVar[int] = 255
    price_format_min_length: ClassVar[int] = 1
    price_format_max_length: ClassVar[int] = 80

    has_dynamic_content: bool
    id: int
    name: str
    url: str
    search_url: str
    search_result_css: str
    image_css: str
    isbn_css: str
    price_css: str
    price_format: str
    form_action_url: str
    return_url: str
    errors: dict[str, list[str]] = dataclasses.field(default_factory=lambda: defaultdict(list))

    def add_error(self, field_name: str, message: str) -> None:
        self.errors[field_name].append(message)

    def is_valid(self) -> bool:
        if not self.errors:
            self._validate_input()

        return not self.errors

    def _validate_input(self) -> None:
        if not length_equals_or_longer_than(self.name, self.name_min_length):
            self.errors[self.name_field_name].append(
                min_length_not_met("Navnet", self.name_min_length))
        elif not length_equals_or_shorter_than(self.name, self.name_max_length):
            self.errors[self.name_field_name].append(
                max_length_exceeded("Navnet", self.name_max_length))

        if not length_equals_or_longer_than(self.url, self.url_min_length):
            self.errors[self.url_field_name].append(
                min_length_not_met("URL", self.url_min_length))
        elif not length_equals_or_shorter_than(self.url, self.url_max_length):
            self.errors[self.url_field_name].append(
                max_length_exceeded("URL", self.url_max_length))

        if not length_equals_or_longer_than(self.search_url, self.search_url_min_length, allow_none=True):
            self.errors[self.search_url_field_name].append(
                min_length_not_met("URL til søgning", self.search_url_min_length))
        elif not length_equals_or_shorter_than(self.search_url, self.search_url_max_length, allow_none=True):
            self.errors[self.search_url_field_name].append(
                max_length_exceeded("URL til søgning", self.search_url_max_length))

        if not length_equals_or_longer_than(self.search_result_css, self.search_result_css_min_length, allow_none=True):
            self.errors[self.search_result_css_field_name].append(
                min_length_not_met("CSS-selektor for søgeresultater", self.search_result_css_min_length))
        elif not length_equals_or_shorter_than(
                self.search_result_css, self.search_result_css_max_length, allow_none=True):
            self.errors[self.search_result_css_field_name].append(
                max_length_exceeded("CSS-selektor for søgeresultater", self.search_result_css_max_length))

        if not length_equals_or_longer_than(self.isbn_css, self.isbn_css_min_length, allow_none=True):
            self.errors[self.isbn_css_field_name].append(
                min_length_not_met("CSS-selektor til ISBN-13", self.isbn_css_min_length))
        elif not length_equals_or_shorter_than(self.isbn_css, self.isbn_css_max_length, allow_none=True):
            self.errors[self.isbn_css_field_name].append(
                max_length_exceeded("CSS-selektor til ISBN-13", self.isbn_css_max_length))

        if not length_equals_or_longer_than(self.price_css, self.price_format_min_length, allow_none=True):
            self.errors[self.price_css_field_name].append(
                min_length_not_met("CSS-selektor for priser", self.price_css_min_length))
        elif not length_equals_or_shorter_than(self.price_css, self.price_css_max_length, allow_none=True):
            self.errors[self.price_css_field_name].append(
                max_length_exceeded("CSS-selektor for priser", self.price_css_max_length))

        if not length_equals_or_longer_than(self.image_css, self.image_css_min_length, allow_none=True):
            self.errors[self.image_css_field_name].append(
                min_length_not_met("CSS-selektor for billeder", self.image_css_min_length))
        elif not length_equals_or_shorter_than(self.image_css, self.image_css_max_length, allow_none=True):
            self.errors[self.image_css_field_name].append(
                max_length_exceeded("CSS-selektor for billeder", self.image_css_max_length))
