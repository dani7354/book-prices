from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import Currency
from bookprices.shared.repository.base import RepositoryBase


class CurrencyRepository(RepositoryBase[Currency]):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return Currency

    def get_by_code(self, code: str) -> Currency | None:
        currency = self._session.execute(select(Currency).filter_by(code=code)).scalar_one_or_none()
        self._session.expunge_all()

        return currency

    def add_or_update(self, entity: Currency) -> None:
        if not (existing_entity := self.get_by_code(entity.code)):
            self.add(entity)
        else:
            self._merge_existing_entity(entity, existing_entity)

    def add_or_update_all(self, entities: list[Currency]) -> None:
        for entity in entities:
            self.add_or_update(entity)

    def update(self, entity: Currency) -> None:
        if not (existing_entity := self.get_by_code(entity.code)):
            raise ValueError(f"Currency with code {entity.code} not found.")

        self._merge_existing_entity(entity, existing_entity)

    def _merge_existing_entity(self, updated_entity: Currency, existing_entity: Currency) -> None:
        existing_entity.rate_to_dkk = updated_entity.rate_to_dkk
        existing_entity.description = updated_entity.description
        existing_entity.updated = updated_entity.updated
        self._session.merge(existing_entity)