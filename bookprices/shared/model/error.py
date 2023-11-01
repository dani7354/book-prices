from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FailedPriceUpdate:
    book_id: int
    book_store_id: int
    error_message: str
    created: datetime
