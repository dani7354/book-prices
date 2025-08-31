from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from bookprices.shared.db.tables import BookList, BookListBook
from bookprices.shared.repository.base import RepositoryBase


class BookListRepository(RepositoryBase[BookList]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookList

    def get(self, entity_id: int) -> BookList | None:
        entity = self._session.get(self.entity_type, entity_id)
        if entity:
            self._session.expunge(entity)
        return entity

    def list_for_user(self, user_id: str) -> list[BookList]:
        booklists_result = (self._session.execute(
            select(self.entity_type)
            .filter_by(user_id=user_id)
            .options(joinedload(BookList.books))
            .order_by(BookList.updated.desc()))
            .scalars()
            .unique()
            .all())
        booklists = []
        for booklist in booklists_result:
            self._session.expunge(booklist)
            booklists.append(booklist)

        return booklists

    def add_book_to_booklist(self, book_id: int, booklist_id: int) -> None:
        booklist_book = BookListBook(book_id=book_id, booklist_id=booklist_id)
        self._session.add(booklist_book)
