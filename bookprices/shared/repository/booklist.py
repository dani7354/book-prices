from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BookList
from bookprices.shared.repository.base import RepositoryBase


class BookListRepository(RepositoryBase[BookList]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookList
