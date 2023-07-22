import pytest
import requests
from unittest.mock import MagicMock
from bookprices.cronjob.update_prices import PriceUpdateJob
from bookprices.shared.model.bookstore import BookInBookStore, BookStore
from bookprices.shared.db.database import Database
import shared


@pytest.fixture
def books_in_bookstore() -> dict[int, list[BookInBookStore]]:
    return {
        1: [
            BookInBookStore(book=MagicMock(),
                            book_store=BookStore(0, "BookStore 1", "http://bookstore1.com",
                            search_url=None,
                            search_result_css_selector=None,
                            price_css_selector=".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)",
                            image_css_selector=None,
                            price_format="\\d+"),
                            url="/book1"),
            BookInBookStore(book=MagicMock(),
                            book_store=BookStore(1, "BookStore 2", "http://bookstore2.com",
                            search_url=None,
                            search_result_css_selector=None,
                            price_css_selector=".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)",
                            image_css_selector=None,
                            price_format="\\d+"),
                            url="/book1"),
        ]
    }


def test_updates_prices_creates_prices(monkeypatch, books_in_bookstore):
    db = Database("", "", "", "", "")
    db.bookstore_db.get_book_stores_for_books = MagicMock(return_value=books_in_bookstore)
    db.book_db.get_books = MagicMock(return_value=[MagicMock()])
    db.bookprice_db.create_prices = MagicMock()
    monkeypatch.setattr(requests, "get", shared.mock_get_price)

    job = PriceUpdateJob(db, thread_count=1)
    job.run()

    args, _ = db.bookprice_db.create_prices.call_args
    assert len(args[0]) == 2
    assert args[0][0].price == 229.0


def test_updates_prices_doesnt_save_if_no_prices_found(monkeypatch, books_in_bookstore):
    db = Database("", "", "", "", "")
    db.bookstore_db.get_book_stores_for_books = MagicMock(return_value={1: [], 2: []})
    db.book_db.get_books = MagicMock(return_value=[MagicMock(), MagicMock()])
    db.bookprice_db.create_prices = MagicMock()
    monkeypatch.setattr(requests, "get", shared.mock_get_price)

    job = PriceUpdateJob(db, thread_count=1)
    job.run()

    assert db.bookprice_db.create_prices.call_count == 0