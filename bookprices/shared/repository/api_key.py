from sqlalchemy.orm import Session

from bookprices.shared.db.tables import ApiKey
from bookprices.shared.repository.base import RepositoryBase


class ApiKeyRepository(RepositoryBase[ApiKey]):
    """ Repository for Job Api keys. """

    def __init__(self, session: Session) -> None:
        super().__init__(session)


    @property
    def entity_type(self) -> type:
        return ApiKey

    def get_by_name(self, api_name: str) -> ApiKey | None:
        entity = self._session.query(self.entity_type).filter_by(api_name=api_name).first()
        self._session.expunge_all()

        return entity

    def update(self, entity: ApiKey) -> None:
        if not (existing_entity := self._session.get(self.entity_type, entity.id)):
            raise ValueError(f"ApiKey with id {entity.id} not found")

        existing_entity.api_name = entity.api_name
        existing_entity.api_user = entity.api_user
        existing_entity.api_key = entity.api_key
        self._session.merge(existing_entity)
