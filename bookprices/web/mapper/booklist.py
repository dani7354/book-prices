from typing import Sequence

from flask import url_for

from bookprices.shared.db.tables import BookList
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.booklist import BookListIndexViewModel, BookListItemViewModel, BookListDetailsViewModel


BOOKLIST_ITEM_DESCRIPTION_LENGTH = 100


def _get_description_for_booklist_item(booklist: BookList) -> str | None:
    if (description_length := len(booklist.description)) > BOOKLIST_ITEM_DESCRIPTION_LENGTH:
        try:
            description_end_index = booklist.description[BOOKLIST_ITEM_DESCRIPTION_LENGTH:].index(" ")
        except ValueError:
            description_end_index = BOOKLIST_ITEM_DESCRIPTION_LENGTH
        description = f"{booklist.description[:description_end_index]}..."
    elif description_length > 0:
        description_end_index = description_length
        description = booklist.description[:description_end_index]
    else:
        description = None

    return description


def map_booklist_item(booklist: BookList) -> BookListItemViewModel:
    description = _get_description_for_booklist_item(booklist)

    return BookListItemViewModel(
        id=booklist.id,
        item_count=len(booklist.books),
        name=booklist.name,
        created=booklist.created.isoformat(),
        updated=booklist.updated.isoformat(),
        url=url_for(Endpoint.BOOKLIST_VIEW.value, booklist_id=booklist.id),
        edit_url=url_for(Endpoint.BOOKLIST_EDIT.value, booklist_id=booklist.id),
        description=description
    )


def map_to_booklist_list(booklists: Sequence[BookList]) -> BookListIndexViewModel:
    return BookListIndexViewModel(
        create_url=url_for(Endpoint.BOOKLIST_CREATE.value),
        booklists=[
            BookListItemViewModel(
                id=booklist.id,
                item_count=len(booklist.books),
                name=booklist.name,
                created=booklist.created.isoformat(),
                updated=booklist.updated.isoformat(),
                url=url_for(Endpoint.BOOKLIST_VIEW.value, booklist_id=booklist.id),
                edit_url=url_for(Endpoint.BOOKLIST_EDIT.value, booklist_id=booklist.id),
                description=booklist.description[:100] if booklist.description else None
            ) for booklist in booklists
        ]
    )


def map_to_details_view_model(booklist: BookList) -> BookListDetailsViewModel:
    return BookListDetailsViewModel(
        books=[],
        return_url=url_for(Endpoint.BOOKLIST_INDEX.value),
        name=booklist.name,
        created=booklist.created.isoformat(),
        updated=booklist.updated.isoformat(),
        description=booklist.description
    )
