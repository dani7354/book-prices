from hashlib import md5
from typing import Optional


def get_authors_key() -> str:
    return "authors"


def get_book_key(book_id: int) -> str:
    return f"book_{book_id}"


def get_book_latest_prices_key(book_id: int) -> str:
    return f"book_latest_prices_{book_id}"


def get_book_in_book_store_key(book_id: int, store_id: int) -> str:
    return f"book_{book_id}_store_{store_id}"


def get_book_list_key(page_id: int, search: Optional[str] = None, author: Optional[str] = None) -> str:
    return md5(f"book_list_{page_id}_{search}_{author}".encode()).hexdigest()
