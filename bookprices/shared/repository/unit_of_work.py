from sqlalchemy.orm import Session

from bookprices.shared.repository.book import BookRepository
from bookprices.shared.repository.booklist import BookListRepository
from bookprices.shared.repository.bookstore import BookStoreRepository
from bookprices.web.shared.db_session import SessionFactory


class UnitOfWork:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.booklist_repository: BookListRepository | None = None
        self.book_repository: BookRepository | None = None
        self.bookstore_repository: BookStoreRepository | None = None

    def __enter__(self) -> "UnitOfWork":
        try:
            self._session = self._session_factory.create_session()
            self.booklist_repository = BookListRepository(self._session)
            self.book_repository = BookRepository(self._session)
            self.bookstore_repository = BookStoreRepository(self._session)
            return self
        except Exception:
            if self._session:
                self._session.rollback()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val:
            self._session.rollback()
        else:
            self._session.commit()
        self._session.close()