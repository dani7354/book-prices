from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select, case, delete
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

    def delete_prices(self, ids: list[int]) -> None:
        self._session.execute(delete(BookPrice).where(BookPrice.id.in_(ids)))

    def get_price_count_by_bookstore(self, from_date: datetime) -> list[tuple[int, str, int]]:
        price_count = func.count(case((BookPrice.created >= from_date, 1)))
        stmt = (
            select(BookStore.id, BookStore.name, price_count)
                   .outerjoin(BookPrice, BookPrice.book_store_id == BookStore.id)
                   .group_by(BookStore.id, BookStore.name)
                   .order_by(price_count.desc()))

        return [(row[0], row[1], row[2]) for row in self._session.execute(stmt).all()]

    def get_prices_for_book_by_bookstore_id(self, book_id: int) -> dict[int, list[tuple[int, int, int, float, datetime]]]:
        latest_prices = (
            select(func.max(BookPrice.id).label("id"))
            .where(BookPrice.book_id == book_id)
            .group_by(func.date(BookPrice.created), BookPrice.book_store_id)
            .cte("latest_prices"))

        stmt = (
            select(
                BookPrice.id,
                BookPrice.book_id,
                BookPrice.book_store_id,
                BookPrice.price,
                func.date(BookPrice.created).label("created"))
            .join(latest_prices, BookPrice.id == latest_prices.c.id)
            .order_by(func.date(BookPrice.created).desc())
        )

        prices_by_bookstore_id = defaultdict(list)
        for row in self._session.execute(stmt).all():
            prices_by_bookstore_id[row[2]].append((row[0], row[1], row[2], row[3], row[4]))

        return prices_by_bookstore_id