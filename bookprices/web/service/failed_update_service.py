from flask_caching import Cache
from bookprices.shared.db.database import Database
from bookprices.web.cache.key_generator import get_failed_count_by_reason_key


class FailedUpdateService:
    def __init__(self, db: Database, cache: Cache):
        self._db = db
        self._cache = cache

    def get_failed_price_updates_by_bookstore(self):
        if failed_counts := self._cache.get(get_failed_count_by_reason_key()):
            return failed_counts
        failed_count = self._db.bookprice_db.get_failed_price_update_count_by_reason()
        if failed_count:
            self._cache.set(get_failed_count_by_reason_key(), failed_count)

        return failed_count


