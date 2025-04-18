from enum import StrEnum


class BookPricesEvents(StrEnum):
    BOOK_UPDATED = "book_updated"
    BOOK_DELETED = "book_deleted"
    BOOK_CREATED = "book_created"
    BOOKS_IMPORTED = "books_imported"
    BOOK_PRICE_UPDATED = "book_price_updated"
    BOOKSTORE_SEARCH_COMPLETED = "bookstore_search_completed"



class BookPricesEventsArgName(StrEnum):
    BOOK_ID = "book_id"
    BOOK_IDS = "book_ids"
