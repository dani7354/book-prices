from unittest.mock import Mock

import pytest
from datetime import datetime, timedelta
from bookprices.jobrunner.job.trim_prices import TrimPricesJob
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config.config import Config
from bookprices.shared.db.bookprice import BookPriceDb
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.bookstore import BookStore


def _generate_prices(count: int) -> list[BookPrice]:
    return [BookPrice(
            id=i,
            book=Mock(Book),
            book_store=Mock(BookStore),
            price=100.5,
            created=datetime.now() - timedelta(days=count - i)) for i in range(count)]


@pytest.fixture
def job() -> TrimPricesJob:
    return TrimPricesJob(Mock(Config), Mock(BookPriceKeyRemover), Mock(BookPriceDb))


def test_get_prices_to_remove_no_prices_deleted(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(job.min_prices_to_keep))

    prices_to_delete = job.get_prices_to_remove(prices)

    assert {x.id for x in prices_to_delete} == set()
    assert len(prices) - len(prices_to_delete) == job.min_prices_to_keep


def test_get_prices_to_remove_no_prices_deleted_if_empty(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(0))

    prices_to_delete = job.get_prices_to_remove(prices)

    assert {x.id for x in prices_to_delete} == set()
    assert not prices_to_delete


def test_get_prices_to_remove_one_deleted(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(job.min_prices_to_keep + 1))

    prices_to_delete = job.get_prices_to_remove(prices)

    assert {x.id for x in prices_to_delete} == {1}
    assert len(prices) - len(prices_to_delete) == job.min_prices_to_keep


def test_get_prices_to_remove_three_deleted(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(job.min_prices_to_keep + 3))

    price = prices[1]
    prices[1] = BookPrice(id=price.id, book=price.book, book_store=price.book_store, price=100.0, created=price.created)
    prices_to_delete = job.get_prices_to_remove(prices)

    assert {x.id for x in prices_to_delete} == {3,4,5}
    assert len(prices) - len(prices_to_delete) == job.min_prices_to_keep


def test_get_prices_to_remove_no_prices_deleted_if_no_redundant_updates(job: TrimPricesJob) -> None:
    total_price_count = job.min_prices_to_keep + 100
    prices = list(_generate_prices(total_price_count))

    for i, p in enumerate(prices):
        prices[i] = BookPrice(id=p.id, book=p.book, book_store=p.book_store, price=100.0 + i, created=p.created)

    prices_to_delete = job.get_prices_to_remove(prices)

    assert {x.id for x in prices_to_delete} == set()
    assert len(prices) - len(prices_to_delete) == total_price_count


def test_get_prices_to_remove_many_deleted_but_not_the_first_update(job: TrimPricesJob) -> None:
    total_price_count = job.min_prices_to_keep + 100
    prices = list(_generate_prices(total_price_count))

    prices_to_delete = job.get_prices_to_remove(prices)

    assert len(prices) - len(prices_to_delete) == job.min_prices_to_keep
    price_ids_to_delete = {x.id for x in prices_to_delete}
    assert prices[0].id not in price_ids_to_delete
    assert prices[-1].id not in price_ids_to_delete
