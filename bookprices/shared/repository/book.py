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

    def create(self, entity: Book) -> int:
        self._session.add(entity)
        self._session.flush()

        return entity.id

    def update(self, entity: Book) -> None:
        existing_book = self._session.get(Book, entity.id)
        if not existing_book:
            raise ValueError(f"Book with id {entity.id} not found.")

        existing_book.isbn = entity.isbn
        existing_book.format = entity.format
        existing_book.title = entity.title
        existing_book.author = entity.author

        self._session.merge(existing_book)

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

    def list_books_by_isbn(self) -> dict[str, Book]:
        books = (self._session.execute(select(Book)).scalars().all())
        self._session.expunge_all()
        books_by_isbn = {book.isbn: book for book in books}

        return books_by_isbn
