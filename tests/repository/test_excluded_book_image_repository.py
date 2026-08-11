import pytest

from bookprices.shared.db.tables import ExcludedBookImage
from bookprices.shared.repository.excluded_book_image import ExcludedBookImageRepository


@pytest.fixture
def excluded_book_image_repository(data_session) -> ExcludedBookImageRepository:
    return ExcludedBookImageRepository(data_session)


@pytest.fixture
def excluded_book_image() -> ExcludedBookImage:
    return ExcludedBookImage(
        hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        reason="test exclusion")


def test_create_and_list_excluded_book_image(
        excluded_book_image_repository: ExcludedBookImageRepository,
        excluded_book_image: ExcludedBookImage) -> None:
    excluded_book_image_repository.add(excluded_book_image)
    excluded_book_image_repository._session.commit()

    excluded_images = excluded_book_image_repository.list_excluded_images()

    assert excluded_images
    first = excluded_images[0]
    assert first.hash == excluded_book_image.hash
    assert first.reason == excluded_book_image.reason


def test_is_book_image_excluded(
        excluded_book_image_repository: ExcludedBookImageRepository,
        excluded_book_image: ExcludedBookImage) -> None:
    excluded_book_image_repository.add(excluded_book_image)
    excluded_book_image_repository._session.commit()

    assert excluded_book_image_repository.is_book_image_excluded(excluded_book_image.hash)
    assert not excluded_book_image_repository.is_book_image_excluded("not-present")
