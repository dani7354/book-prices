from typing import Sequence, Generator
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


def test_get_prices_to_remove_one_deleted(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(job.min_prices_to_keep + 1))

    prices_to_delete = job.get_prices_to_remove(prices)
    assert {x.id for x in prices_to_delete} == {1}


def test_get_prices_to_remove_three_deleted(job: TrimPricesJob) -> None:
    prices = list(_generate_prices(job.min_prices_to_keep + 3))

    price = prices[1]
    prices[1] = BookPrice(id=price.id, book=price.book, book_store=price.book_store, price=100.0, created=price.created)
    prices_to_delete = job.get_prices_to_remove(prices)
    assert {x.id for x in prices_to_delete} == {3,4,5}
