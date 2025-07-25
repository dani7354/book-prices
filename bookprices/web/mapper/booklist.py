from typing import Sequence

from flask import url_for

from bookprices.shared.db.tables import BookList
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.booklist import BookListIndexViewModel, BookListItemViewModel, BookListDetailsViewModel


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
                url=url_for(Endpoint.BOOKLIST_VIEW.value, booklist_id=booklist.id)
            ) for booklist in booklists
        ]
    )


def map_to_details_view_model(booklist: BookList) -> BookListDetailsViewModel:
    return BookListDetailsViewModel(
        books=[],
        return_url=url_for(Endpoint.BOOKLIST_INDEX.value),
        name=booklist.name,
        created=booklist.created.isoformat(),
        updated=booklist.updated.isoformat()
    )
