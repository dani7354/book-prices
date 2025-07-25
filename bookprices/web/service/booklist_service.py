import logging
from datetime import datetime

from flask_caching import Cache

from bookprices.shared.cache.key_generator import get_booklists_for_user_key, get_booklist_key
from bookprices.shared.db.tables import BookList
from bookprices.shared.repository.unit_of_work import UnitOfWork


class BookListService:
    """ Service for book list related functionality. """

    def __init__(self, unit_of_work: UnitOfWork, cache: Cache) -> None:
        self._unit_of_work = unit_of_work
        self._cache = cache
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_booklist(self, booklist_id: int, user_id: str) -> BookList | None:
        """ Retrieves a book list by its ID. """
        if not (booklist := self._cache.get(get_booklist_key(booklist_id))):
            with self._unit_of_work:
                booklist = self._unit_of_work.booklist_repository.get(booklist_id)
                if booklist:
                    self._cache.set(get_booklist_key(booklist_id), booklist)

        if booklist and booklist.user_id != user_id:
            self._logger.warning(f"User with id {user_id} attempted to access booklist {booklist_id}, "
                                 f"which belongs to another user.")
            return None

        return booklist

    def get_booklists(self, user_id: str) -> list[BookList]:
        if not (booklists := self._cache.get(get_booklists_for_user_key(user_id))):
            with self._unit_of_work:
                booklists = self._unit_of_work.booklist_repository.list_for_user(user_id)
                if booklists:
                    self._cache.set(get_booklists_for_user_key(user_id), booklists)

        return booklists

    def create_booklist(self, name: str, user_id) -> None:
        """ Creates a new book list. """
        booklist = BookList(
            id=0,
            name=name,
            user_id=user_id,
            created=datetime.now(),
            updated=datetime.now())

        with self._unit_of_work:
            self._unit_of_work.booklist_repository.add(booklist)

        self._cache.delete(get_booklists_for_user_key(user_id))
        self._logger.info(f"Created new book list '{name}' for user {user_id}.")

    def name_available(self, name: str, user_id: str) -> bool:
        booklists = self.get_booklists(user_id)
        return not any([b for b in booklists if b.name == name])

    def add_book(self, book_id: int, booklist_id: int, user_id: str) -> bool:
        if not (_ := self.get_booklist(booklist_id, user_id)):
            self._logger.error(
                f"User {user_id} failed to access {booklist_id}. Either it does not exist or does not belong to the user.")
            return False

        with self._unit_of_work:
            if not (_ := self._unit_of_work.book_repository.get(book_id)):
                self._logger.error(f"Book with id {book_id} does not exist.")
                return False

            self._unit_of_work.booklist_repository.add_book_to_booklist(book_id, booklist_id)

        return True


