from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import FailedPriceUpdate, BookStore
from bookprices.shared.repository.base import RepositoryBase


class FailedPriceUpdateRepository(RepositoryBase[FailedPriceUpdate]):

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return FailedPriceUpdate

    def update(self, entity: FailedPriceUpdate) -> None:
        if not (existing_entity := self._session.get(FailedPriceUpdate, entity.id)):
            raise ValueError(f"FailedPriceUpdate with id {entity.id} not found.")

        existing_entity.reason = entity.reason
        existing_entity.book_price_id = entity.book_store_id
        existing_entity.book_id = entity.book_id

        self._session.add(existing_entity)

    def get_failed_update_count_by_reason(self, date_from: datetime) -> list[tuple[str, int]]:
        stmt = (select(
                FailedPriceUpdate.reason,
                func.count(FailedPriceUpdate.id))
            .outerjoin(BookStore, FailedPriceUpdate.book_store_id == BookStore.id)
            .group_by((FailedPriceUpdate.reason, BookStore.id))
            .where(FailedPriceUpdate.created >= date_from)
            .order_by(func.count(FailedPriceUpdate.id).desc()))

        return [(row[0], row[1]) for row in self._session.execute(stmt).all()]
