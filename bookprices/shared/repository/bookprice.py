from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BookPrice
from bookprices.shared.repository.base import RepositoryBase


class BookPriceRepository(RepositoryBase[BookPrice]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookPrice

    def update(self, entity: BookPrice) -> None:
        raise NotImplementedError

    def add_prices(self, entities: list[BookPrice]) -> None:
        self._session.bulk_save_objects(entities)