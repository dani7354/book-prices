from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BookList, BookListBook
from bookprices.shared.repository.base import RepositoryBase


class BookListRepository(RepositoryBase[BookList]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookList

    def list_for_user(self, user_id: str) -> list[BookList]:
        booklists_result = self._session.execute(
            select(self.entity_type).filter_by(user_id=user_id).order_by(BookList.updated.desc())).scalars().unique().all()
        booklists = []
        for booklist in booklists_result:
            self._session.expunge(booklist)
            booklists.append(booklist)

        return booklists

    def add_book_to_booklist(self, book_id: int, booklist_id: int) -> None:
        booklist_book = BookListBook(book_id=book_id, booklist_id=booklist_id)
        self._session.add(booklist_book)
