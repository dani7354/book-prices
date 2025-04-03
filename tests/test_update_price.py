import pytest
import requests
from unittest.mock import MagicMock
from bookprices.job.job.update_prices import BookPricesUpdateJob
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.model.bookstore import BookInBookStore, BookStore
from bookprices.shared.db.database import Database
from fake.cache import FakeCacheClient
import shared


@pytest.fixture
def books_in_bookstore() -> dict[int, list[BookInBookStore]]:
    return {
        1: [
            BookInBookStore(book=MagicMock(),
                            book_store=BookStore(0, "BookStore 1", "https://bookstore1.com",
                            search_url=None,
                            search_result_css_selector=None,
                            price_css_selector=".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)",
                            image_css_selector=None,
                            price_format="\\d+",
                            has_dynamically_loaded_content=False,
                            isbn_css_selector=None),
                            url="/book1"),
            BookInBookStore(book=MagicMock(),
                            book_store=BookStore(1, "BookStore 2", "https://bookstore2.com",
                            search_url=None,
                            search_result_css_selector=None,
                            price_css_selector=".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)",
                            image_css_selector=None,
                            price_format="\\d+",
                            has_dynamically_loaded_content=False,
                            isbn_css_selector=None),
                            url="/book1"),
        ]
    }


@pytest.fixture
def cache_key_remover():
    fake_cache_client = FakeCacheClient()
    cache_key_remover = BookPriceKeyRemover(fake_cache_client)

    return cache_key_remover


def test_updates_prices_creates_prices(monkeypatch, books_in_bookstore, cache_key_remover):
    db = Database("", "", "", "", "")
    db.bookstore_db.get_bookstores_for_books = MagicMock(return_value=books_in_bookstore)
    db.book_db.get_books_by_ids = MagicMock(return_value=[MagicMock()])
    db.book_db.get_book_count = MagicMock(return_value=1)
    db.book_db.get_next_book_ids = MagicMock(return_value=[1])
    db.bookprice_db.create_prices = MagicMock()
    monkeypatch.setattr(requests, "get", lambda url, allow_redirects: shared.create_fake_response("price_format.html"))

    job = PriceUpdateJob(db, cache_key_remover, thread_count=1)
    job.run()

    args, _ = db.bookprice_db.create_prices.call_args
    assert len(args[0]) == 2
    assert args[0][0].price == 229


def test_updates_prices_doesnt_save_if_no_prices_found(monkeypatch, books_in_bookstore, cache_key_remover):
    db = Database("", "", "", "", "")
    db.bookstore_db.get_bookstores_for_books = MagicMock(return_value={1: [], 2: []})
    db.book_db.get_books_by_ids = MagicMock(return_value=[MagicMock()])
    db.book_db.get_book_count = MagicMock(return_value=1)
    db.book_db.get_next_book_ids = MagicMock(return_value=[1])
    db.bookprice_db.create_prices = MagicMock()
    monkeypatch.setattr(requests, "get", lambda x: shared.create_fake_response("price_format.html"))

    job = PriceUpdateJob(db, cache_key_remover, thread_count=1)
    job.run()

    assert db.bookprice_db.create_prices.call_count == 0
