from typing import Sequence

from flask import url_for

from bookprices.shared.db.tables import BookList
from bookprices.web.shared.enum import Endpoint
from bookprices.web.viewmodels.booklist import BookListIndexViewModel, BookListItemViewModel


def map_to_booklist_list(booklists: Sequence[BookList]) -> BookListIndexViewModel:
    """ Maps a sequence of BookList objects to a BookListIndexViewModel. """
    return BookListIndexViewModel(
        create_url=url_for(Endpoint.BOOKLIST_CREATE.value),
        booklists=[
            BookListItemViewModel(
                id=booklist.id,
                name=booklist.name,
                created=booklist.created.isoformat(),
                updated=booklist.updated.isoformat(),
                url=url_for(Endpoint.BOOKLIST_VIEW.value, booklist_id=booklist.id)
            ) for booklist in booklists
        ]
    )