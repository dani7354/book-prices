from sqlalchemy.orm import Session, scoped_session

from bookprices.shared.repository.book import BookRepository
from bookprices.shared.repository.booklist import BookListRepository
from bookprices.shared.repository.bookprice import BookPriceRepository
from bookprices.shared.repository.bookstore import BookStoreRepository
from bookprices.shared.db.data_session import SessionFactory
from bookprices.shared.repository.currency import CurrencyRepository


class UnitOfWork:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.booklist_repository: BookListRepository | None = None
        self.book_repository: BookRepository | None = None
        self.bookstore_repository: BookStoreRepository | None = None
        self.bookprice_repository: BookPriceRepository | None = None
        self.currency_repository: CurrencyRepository | None = None

    def __enter__(self) -> "UnitOfWork":
        try:
            self._session = self._session_factory.create_scoped_session()
            self.booklist_repository = BookListRepository(self._session)
            self.book_repository = BookRepository(self._session)
            self.bookstore_repository = BookStoreRepository(self._session)
            self.bookprice_repository = BookPriceRepository(self._session)
            self.currency_repository = CurrencyRepository(self._session)
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