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
