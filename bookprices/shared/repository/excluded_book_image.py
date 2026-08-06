from sqlalchemy import select
from sqlalchemy.orm import Session

from bookprices.shared.db.tables import ExcludedBookImage
from bookprices.shared.repository.base import RepositoryBase


class ExcludedBookImageRepository(RepositoryBase):
    """ Repository class for images excluded from download and usage in the web app. """

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return ExcludedBookImage

    def update(self, entity: ExcludedBookImage) -> None:
        raise NotImplementedError

    def is_book_image_excluded(self, image_hash: str) -> bool:
        return self._session.scalar(select(ExcludedBookImage).where(ExcludedBookImage.hash == image_hash)) is not None

    def list_excluded_images(self) -> list[ExcludedBookImage]:
        return list(self._session.scalars(select(ExcludedBookImage)).all())