import pytest

from bookprices.shared.db.tables import BookStore
from bookprices.shared.repository.bookstore import BookStoreRepository


@pytest.fixture
def bookstore_repository(data_session) -> BookStoreRepository:
    return BookStoreRepository(data_session)


@pytest.fixture
def bookstore() -> BookStore:
    return BookStore(
        name="TestBookStore 0",
        url="https://testbookstore1.com",
        search_url="https://testbookstore1.com/search?q={0}",
        search_result_css_selector=".search-result",
        price_css_selector=".price",
        image_css_selector=".image",
        isbn_css_selector=".isbn",
        color_hex="000000",
        price_format="\d+",
        scraper_id="ScraperId0")


def test_create_and_list_bookstore(
        bookstore_repository: BookStoreRepository,
        bookstore: BookStore) -> None:
    bookstore_repository.add(bookstore)
    bookstore_repository._session.commit()

    bookstore_list = bookstore_repository.get_list()

    assert bookstore_list
    first_bookstore = bookstore_list[0]
    assert first_bookstore.id == 1
    assert first_bookstore.url == bookstore.url
    assert first_bookstore.name == bookstore.name
    assert first_bookstore.search_url == bookstore.search_url
    assert first_bookstore.price_format == bookstore.price_format
    assert first_bookstore.color_hex == bookstore.color_hex
    assert first_bookstore.image_css_selector == bookstore.image_css_selector
    assert first_bookstore.search_result_css_selector == bookstore.search_result_css_selector
    assert first_bookstore.price_css_selector == bookstore.price_css_selector
    assert first_bookstore.scraper_id == bookstore.scraper_id


def test_update_bookstore(
        bookstore_repository: BookStoreRepository,
        bookstore: BookStore) -> None:
    bookstore_repository.add(bookstore)
    bookstore_repository._session.commit()

    bookstore_id, bookstore_new_name = 1, "UpdatedName"
    new_bookstore = bookstore_repository.get(bookstore_id)
    new_bookstore.name = bookstore_new_name
    bookstore_repository.update(new_bookstore)
    bookstore_repository._session.commit()

    updated_bookstore = bookstore_repository.get(bookstore_id)
    assert updated_bookstore.name == bookstore_new_name


def test_delete_bookstore(
        bookstore_repository: BookStoreRepository,
        bookstore: BookStore) -> None:
    bookstore_repository.add(bookstore)
    bookstore_repository._session.commit()
    assert bookstore_repository.get_list()

    bookstore_repository.delete(1)
    bookstore_repository._session.commit()
    assert not bookstore_repository.get_list()
