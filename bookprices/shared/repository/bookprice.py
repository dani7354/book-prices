from datetime import datetime

from sqlalchemy import func, select, case
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BookPrice, BookStore
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

    def get_price_count_by_bookstore(self, from_date: datetime) -> list[tuple[int, str, int]]:
        price_count = func.count(case((BookPrice.created >= from_date, 1)))
        stmt = (
            select(BookStore.id, BookStore.name, price_count)
                   .outerjoin(BookPrice, BookPrice.book_store_id == BookStore.id)
                   .group_by(BookStore.id, BookStore.name)
                   .order_by(price_count.desc()))

        return [(row[0], row[1], row[2]) for row in self._session.execute(stmt).all()]