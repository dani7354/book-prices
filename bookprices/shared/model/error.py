from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class FailedUpdateReason(Enum):
    CONNECTION_ERROR = "CONNECTION_ERROR"
    PAGE_NOT_FOUND = "PAGE_NOT_FOUND"
    INVALID_PRICE_FORMAT = "INVALID_PRICE_FORMAT"
    PRICE_SELECT_ERROR = "PRICE_SELECT_ERROR"

    @staticmethod
    def from_str(value: str):
        for reason in FailedUpdateReason:
            if reason.value == value:
                return reason
        raise ValueError(f"Failed parsing value: {value}")


@dataclass
class FailedPriceUpdate:
    id: Optional[int]
    book_id: int
    bookstore_id: int
    reason: FailedUpdateReason
    created: datetime


@dataclass
class FailedPriceUpdateCount:
    book_id: int
    bookstore_id: int
    count: int
