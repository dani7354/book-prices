from flask_caching import Cache
from datetime import timedelta, datetime
from bookprices.shared.db.database import Database
from bookprices.shared.model.status import FailedPriceUpdateCountByReason, BookImportCount, PriceCount
from bookprices.shared.cache.key_generator import (
    get_failed_count_by_reason_key, get_book_import_count_key, get_price_count_key)
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.shared.enum import CacheTtlOption
from bookprices.web.viewmodels.status import TimePeriodSelectOption, UpdatedPricesForBookStoreResponse, TableResponse


class StatusService:
    """ Service for getting status information for the site dashboard. """

    def __init__(self, db: Database, unit_of_work: UnitOfWork, cache: Cache) -> None:
        self._db = db
        self._unit_of_work = unit_of_work
        self._cache = cache

    def get_failed_price_updates_by_bookstore(self, days: int) -> list[FailedPriceUpdateCountByReason]:
        date_from = datetime.now() - timedelta(days=days)
        if failed_counts := self._cache.get(get_failed_count_by_reason_key(date_from)):
            return failed_counts
        if failed_count := self._db.status_db.get_failed_price_update_count_by_reason(date_from):
            self._cache.set(
                get_failed_count_by_reason_key(date_from), failed_count, timeout=CacheTtlOption.MEDIUM.value)

        return failed_count

    def get_book_import_count_by_bookstore(self, days: int) -> list[BookImportCount]:
        date_from = datetime.now() - timedelta(days=days)
        if import_counts := self._cache.get(get_book_import_count_key(date_from)):
            return import_counts
        if import_counts := self._db.status_db.get_book_import_count_by_bookstore(date_from):
            self._cache.set(get_book_import_count_key(date_from), import_counts, timeout=CacheTtlOption.MEDIUM.value)

        return import_counts

    def get_price_count_by_bookstore(self, days: int) -> list[PriceCount]:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_price_count_key(date_from)
        if price_counts := self._cache.get(cache_key):
            return price_counts
        if price_counts := self._db.status_db.get_price_count_by_bookstore(date_from):
            self._cache.set(cache_key, price_counts, timeout=CacheTtlOption.MEDIUM.value)

        return price_counts

    def get_updated_prices_by_for_bookstores(self, days: int) -> UpdatedPricesForBookStoreResponse:
        with self._unit_of_work as uow:
            date_from = datetime.now() - timedelta(days=days)
            updated_prices = uow.bookstore_repository.get_bookstores_with_updated_prices_percentage(date_from)

        columns, rows = [], []
        translations = {}
        for bookstore_id, bookstore_name, book_count, updated_prices, updated_percentage in updated_prices:
            rows.append({
                "book_store": bookstore_name,
                "book_count": book_count,
                "updated_prices": updated_prices,
                "updated_percentage": f"{updated_percentage:.2f}%"
            })

        columns.extend(rows[0].keys() if rows else [])
        table_response = TableResponse(title="Opdaterede priser", columns=columns, rows=rows)

        return UpdatedPricesForBookStoreResponse(translations=translations, table=table_response)



    @staticmethod
    def get_timeperiod_options() -> list[TimePeriodSelectOption]:
        timeperiod_options = [
            TimePeriodSelectOption(text="1 dag", days=1),
            TimePeriodSelectOption(text="7 dage", days=7),
            TimePeriodSelectOption(text="14 dage", days=14),
            TimePeriodSelectOption(text="30 dage", days=30),
            TimePeriodSelectOption(text="90 dage", days=90),
            TimePeriodSelectOption(text="365 dage", days=365),
        ]

        return timeperiod_options

