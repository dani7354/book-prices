from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BookList
from bookprices.shared.repository.base import RepositoryBase


class BookListRepository(RepositoryBase[BookList]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookList

    def list_for_user(self, user_id: str) -> list[BookList]:
        booklists_result = self._session.execute(select(self.entity_type).filter_by(user_id=user_id)).scalars().all()
        booklists = []
        for booklist in booklists_result:
            self._session.expunge(booklist)
            booklists.append(booklist)

        return booklists
