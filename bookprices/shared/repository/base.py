from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BaseModel


T = TypeVar('T', bound=BaseModel)


class RepositoryBase(Generic[T]):
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def entity_type(self) -> type:
        raise NotImplementedError()

    def add(self, entity: T) -> None:
        self._session.add(entity)

    def get(self, entity_id: int) -> T | None:
        entity = self._session.get(self.entity_type, entity_id)
        if entity:
            self._session.expunge(entity)
        return entity

    def update(self, entity: T) -> None:
        self._session.merge(entity)

    def delete(self, entity: T) -> None:
        self._session.delete(entity)

    def list(self) -> list[T]:
        return list(self._session.execute(select(self.entity_type)).scalars().all())
