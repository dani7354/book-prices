from datetime import datetime

from sqlalchemy import select, func, case
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

    def get_failed_update_count_by_reason(self, date_from: datetime) -> list[tuple[int, str, str, int]]:
        failed_update_count = func.count(case((FailedPriceUpdate.created >= date_from, 1)))
        stmt = (select(
                BookStore.id,
                BookStore.name,
                FailedPriceUpdate.reason,
                failed_update_count)
            .outerjoin(FailedPriceUpdate, FailedPriceUpdate.book_store_id == BookStore.id)
            .group_by(BookStore.id, BookStore.name, FailedPriceUpdate.reason)
            .order_by(failed_update_count.desc()))

        return [(row[0], row[1], row[2], row[3] or 0) for row in self._session.execute(stmt).all()]
