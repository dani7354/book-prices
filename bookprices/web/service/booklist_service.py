import logging

from flask_caching import Cache

from bookprices.shared.db.database import Database


class BookListService:
    """ Service for book list related functionality. """

    def __init__(self, database: Database, cache: Cache) -> None:
        self._database = database
        self._cache = cache
        self._logger = logging.getLogger(self.__class__.__name__)

