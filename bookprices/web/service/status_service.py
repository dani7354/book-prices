from flask_caching import Cache
from datetime import timedelta, datetime
from bookprices.shared.db.database import Database
from bookprices.web.cache.key_generator import get_failed_count_by_reason_key
from bookprices.web.viewmodels.status import TimePeriodSelectOption


class StatusService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def get_failed_price_updates_by_bookstore(self, days: int):
        date_from = datetime.now() - timedelta(days=days)
        if failed_counts := self._cache.get(get_failed_count_by_reason_key(date_from)):
            return failed_counts
        failed_count = self._db.bookprice_db.get_failed_price_update_count_by_reason(date_from)
        if failed_count:
            self._cache.set(get_failed_count_by_reason_key(date_from), failed_count)

        return failed_count

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
