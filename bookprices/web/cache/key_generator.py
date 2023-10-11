def get_book_key(book_id: int) -> str:
    return f"book_{book_id}"


def get_book_latest_prices_key(book_id: int) -> str:
    return f"book_latest_prices_{book_id}"


def get_book_in_book_store_key(book_id: int, store_id: int) -> str:
    return f"book_{book_id}_store_{store_id}"