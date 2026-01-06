from bookprices.shared.db.tables import BookStore
from bookprices.shared.repository.base import RepositoryBase


class BookStoreRepository(RepositoryBase[BookStore]):

    def __init__(self, session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookStore