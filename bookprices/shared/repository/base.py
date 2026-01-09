from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import BaseModel


class RepositoryBase[T: BaseModel](ABC):
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    @abstractmethod
    def entity_type(self) -> type:
        raise NotImplementedError()

    def add(self, entity: T) -> None:
        self._session.add(entity)

    def get(self, entity_id: int) -> T | None:
        entity = self._session.get(self.entity_type, entity_id)
        self._session.expunge_all()

        return entity

    @abstractmethod
    def update(self, entity: T) -> None:
        raise NotImplementedError()

    def delete(self, entity_id: int) -> None:
        if not (entity := self._session.get(self.entity_type, entity_id)):
            raise ValueError(f"Entity with id {entity_id} not found.")

        self._session.delete(entity)

    def get_list(self) -> list[T]:
        entities = self._session.execute(select(self.entity_type)).scalars().all()
        self._session.expunge_all()

        return list(entities)
