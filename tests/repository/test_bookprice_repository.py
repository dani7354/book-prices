import pytest
from datetime import datetime

from bookprices.shared.db.tables import BookPrice
from bookprices.shared.repository.bookprice import BookPriceRepository


@pytest.fixture
def bookprice_repository(data_session) -> BookPriceRepository:
    return BookPriceRepository(data_session)


@pytest.fixture
def bookprices() -> list[BookPrice]:
    now = datetime.now()
    return [
        BookPrice(book_id=1, book_store_id=1, price=9.99, created=now),
        BookPrice(book_id=1, book_store_id=2, price=15.75, created=now),
        BookPrice(book_id=1, book_store_id=3, price=8.99, created=now),
        BookPrice(book_id=1, book_store_id=4, price=12.50, created=now)
    ]


def test_create_and_list_bookprice(
        bookprice_repository: BookPriceRepository,
        bookprices: list[BookPrice]) -> None:
    bookprice_repository.add_prices(bookprices)
    bookprice_repository._session.commit()

    price_list = bookprice_repository.get_list()

    assert len(price_list) == 4
    assert price_list[0].price == bookprices[0].price
    assert price_list[1].price == bookprices[1].price
    assert price_list[2].price == bookprices[2].price
    assert price_list[3].price == bookprices[3].price


def test_delete_bookprice(
        bookprice_repository: BookPriceRepository,
        bookprices: list[BookPrice]) -> None:
    bookprice_repository.add(bookprices[0])
    bookprice_repository._session.commit()
    assert bookprice_repository.get_list()

    bookprice_repository.delete(1)
    bookprice_repository._session.commit()
    assert not bookprice_repository.get_list()
