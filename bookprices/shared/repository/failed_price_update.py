from datetime import datetime

from sqlalchemy import select, func, case, delete
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

    def get_latest_failed_price_updates(
            self, book_id: int, bookstore_id: int, limit: int) -> list[tuple[int, int, int, str, datetime]]:
        stmt = (select(
                FailedPriceUpdate.id,
                FailedPriceUpdate.book_id,
                FailedPriceUpdate.book_store_id,
                FailedPriceUpdate.reason,
                FailedPriceUpdate.created)
            .where(FailedPriceUpdate.book_id == book_id)
            .where(FailedPriceUpdate.book_store_id == bookstore_id)
            .order_by(FailedPriceUpdate.created.desc())
            .limit(limit))

        return [(row[0], row[1], row[2], row[3], row[4]) for row in self._session.execute(stmt).all()]

    def get_failed_update_count_above(self, limit: int) -> list[tuple[int, int, int]]:
        stmt = (select(
                FailedPriceUpdate.book_id,
                FailedPriceUpdate.book_store_id,
                func.count(FailedPriceUpdate.id).label("failed_count"))
            .group_by(FailedPriceUpdate.book_id, FailedPriceUpdate.book_store_id)
            .having(func.count(FailedPriceUpdate.id) > limit))

        return [(row[0], row[1], row[2]) for row in self._session.execute(stmt).all()]

    def delete_failed_updates(self, book_id: int, bookstore_id: int) -> None:
        stmt = (delete(FailedPriceUpdate)
                .where(FailedPriceUpdate.book_id == book_id)
                .where(FailedPriceUpdate.book_store_id == bookstore_id))

        self._session.execute(stmt)