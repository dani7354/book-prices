from datetime import datetime
from hashlib import md5
from bookprices.shared.db.book import SearchQuery


KEY_DATE_FORMAT = "%Y-%m-%d"


def get_authors_key() -> str:
    return "authors"


def get_bookstores_key() -> str:
    return "bookstores"


def get_index_latest_books_key() -> str:
    return "index_latest_books"


def get_index_latest_prices_books_key() -> str:
    return "index_latest_prices_books"


def get_book_key(book_id: int) -> str:
    return f"book_{book_id}"


def get_book_latest_prices_key(book_id: int) -> str:
    return f"book_latest_prices_{book_id}"


def get_book_in_book_store_key(book_id: int, store_id: int) -> str:
    return f"book_{book_id}_store_{store_id}"


def get_book_list_key(search_query: SearchQuery) -> str:
    return md5(f"book_list_{search_query.page}_{search_query.search_phrase}_{search_query.author}_"
               f"{search_query.sort_in_descending_order}_{search_query.sort_option.name}".encode()).hexdigest()


def get_user_key(user_id: str) -> str:
    return f"user_{user_id}"


def get_failed_count_by_reason_key(date_from: datetime) -> str:
    date_from_str = date_from.strftime(KEY_DATE_FORMAT)
    return f"failed_count_by_reason_{date_from_str}"


def get_book_import_count_key(date_from: datetime) -> str:
    date_from_str = date_from.strftime(KEY_DATE_FORMAT)
    return f"book_import_count_{date_from_str}"


def get_price_count_key(date_from: datetime) -> str:
    date_from_str = date_from.strftime(KEY_DATE_FORMAT)
    return f"price_count_{date_from_str}"
