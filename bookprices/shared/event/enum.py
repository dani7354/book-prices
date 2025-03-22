from enum import StrEnum


class BookPricesEvents(StrEnum):
    BOOK_UPDATED = "book_updated"
    BOOK_DELETED = "book_deleted"
    BOOK_CREATED = "book_created"
    BOOK_PRICE_UPDATED = "book_price_updated"
