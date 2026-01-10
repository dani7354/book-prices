from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import Book
from bookprices.shared.repository.base import RepositoryBase


class BookRepository(RepositoryBase[Book]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return Book

    def update(self, entity: Book) -> None:
        raise NotImplementedError

    def list_by_id(self, book_ids: Sequence[int]) -> list[Book]:
        entities = self._session.execute(
            select(Book).where(Book.id.in_(book_ids))).scalars().all()
        self._session.expunge_all()

        return list(entities)

    def list_book_ids(self, offset: int, limit: int) -> list[int]:
        book_ids = (self._session.execute(
            select(Book.id)
            .order_by(Book.id)
            .offset(offset)
            .limit(limit))
            .scalars()
            .all())
        self._session.expunge_all()

        return list(book_ids)
