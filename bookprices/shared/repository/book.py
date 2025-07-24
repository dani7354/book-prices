from sqlalchemy.orm import Session

from bookprices.shared.db.tables import Book
from bookprices.shared.repository.base import RepositoryBase


class BookRepository(RepositoryBase[Book]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return Book
