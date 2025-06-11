import dataclasses


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


class BookStoreEditViewModel:
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
