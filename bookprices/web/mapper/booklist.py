from typing import Sequence

from flask import url_for

from bookprices.shared.db.tables import BookList
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.booklist import BookListIndexViewModel, BookListItemViewModel, BookListDetailsViewModel, \
    BookListEditViewModel

BOOKLIST_ITEM_DESCRIPTION_LENGTH = 200


def _get_description_for_booklist_item(booklist: BookList) -> str | None:
    if not booklist.description:
        return None

    description = None
    if (description_length := len(booklist.description)) > BOOKLIST_ITEM_DESCRIPTION_LENGTH:
        try:
            description_end_index = booklist.description[BOOKLIST_ITEM_DESCRIPTION_LENGTH:].index(" ") + BOOKLIST_ITEM_DESCRIPTION_LENGTH
        except ValueError:
            description_end_index = BOOKLIST_ITEM_DESCRIPTION_LENGTH
        description = f"{booklist.description[:description_end_index]}..."
    elif description_length > 0:
        description_end_index = description_length
        description = booklist.description[:description_end_index]

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
        booklists=[map_booklist_item(booklist) for booklist in booklists]
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

def map_to_edit_view_model(booklist: BookList | None, form_action_url: str, return_url: str) -> BookListEditViewModel:
    return BookListEditViewModel(
        name=booklist.name if booklist else "",
        description=booklist.description if booklist else None,
        form_action_url=form_action_url,
        return_url=return_url)
