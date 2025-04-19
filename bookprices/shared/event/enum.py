from enum import StrEnum


class BookPricesEvents(StrEnum):
    BOOK_UPDATED = "book_updated"
    BOOK_CREATED = "book_created"
    BOOK_PRICES_UPDATED = "book_prices_updated"
    BOOKSTORE_SEARCH_COMPLETED = "bookstore_search_completed"
    BOOKS_IMPORTED = "books_imported"
    BOOKS_DELETED = "books_deleted"


class BookPricesEventsArgName(StrEnum):
    BOOK_ID = "book_id"
    BOOK_IDS = "book_ids"
