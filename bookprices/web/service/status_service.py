from flask_caching import Cache
from datetime import timedelta, datetime
from bookprices.shared.db.database import Database
from bookprices.shared.model.status import FailedPriceUpdateCountByReason, BookImportCount, PriceCount
from bookprices.shared.cache.key_generator import (
    get_failed_count_by_reason_key, get_book_import_count_key, get_price_count_key)
from bookprices.web.viewmodels.status import TimePeriodSelectOption


class StatusService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def get_failed_price_updates_by_bookstore(self, days: int) -> list[FailedPriceUpdateCountByReason]:
        date_from = datetime.now() - timedelta(days=days)
        if failed_counts := self._cache.get(get_failed_count_by_reason_key(date_from)):
            return failed_counts
        if failed_count := self._db.status_db.get_failed_price_update_count_by_reason(date_from):
            self._cache.set(get_failed_count_by_reason_key(date_from), failed_count)

        return failed_count

    def get_book_import_count_by_bookstore(self, days: int) -> list[BookImportCount]:
        date_from = datetime.now() - timedelta(days=days)
        if import_counts := self._cache.get(get_book_import_count_key(date_from)):
            return import_counts
        if import_counts := self._db.status_db.get_book_import_count_by_bookstore(date_from):
            self._cache.set(get_book_import_count_key(date_from), import_counts)

        return import_counts

    def get_price_count_by_bookstore(self, days: int) -> list[PriceCount]:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_price_count_key(date_from)
        if price_counts := self._cache.get(cache_key):
            return price_counts
        if price_counts := self._db.status_db.get_price_count_by_bookstore(date_from):
            self._cache.set(cache_key, price_counts)

        return price_counts

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

