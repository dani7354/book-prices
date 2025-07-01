import dataclasses
from typing import ClassVar


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
    has_dynamic_content_field_name: ClassVar[str] = "has_dynamic_content"
    id_field_name: ClassVar[str] = "id"
    name_field_name: ClassVar[str] = "name"
    url_field_name: ClassVar[str] = "url"
    search_url_field_name: ClassVar[str] = "search_url"
    search_result_css_field_name: ClassVar[str] = "search_result_css"
    image_css_field_name: ClassVar[str] = "image_css"
    isbn_css_field_name: ClassVar[str] = "isbn_css"
    price_format_field_name: ClassVar[str] = "price_format"

    has_dynamic_content: bool
    id: int
    name: str
    url: str
    search_url: str
    search_result_css: str
    image_css: str
    isbn_css: str
    price_format: str
    form_action_url: str
    return_url: str
    errors: dict[str, list[str]] = dataclasses.field(default_factory=dict)
