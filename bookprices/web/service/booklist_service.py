import logging
from datetime import datetime

from flask_caching import Cache

from bookprices.shared.db.database import Database
from bookprices.shared.model.booklist import BookList


class BookListService:
    """ Service for book list related functionality. """

    def __init__(self, database: Database, cache: Cache) -> None:
        self._database = database
        self._cache = cache
        self._logger = logging.getLogger(self.__class__.__name__)

    def create(self, name: str, user_id: str) -> None:
        booklist = BookList(
            id=0,
            name=name,
            user_id=user_id,
            created=datetime.now(),
            updated=datetime.now())


