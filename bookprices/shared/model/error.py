from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FailedUpdateReason(Enum):
    CONNECTION_ERROR = "CONNECTION_ERROR"
    PAGE_NOT_FOUND = "PAGE_NOT_FOUND"
    INVALID_PRICE_FORMAT = "INVALID_PRICE_FORMAT"
    PRICE_SELECT_ERROR = "PRICE_SELECT_ERROR"


@dataclass
class FailedPriceUpdate:
    book_id: int
    bookstore_id: int
    reason: FailedUpdateReason
    created: datetime
