from dataclasses import dataclass
from bookprices.shared.model.error import FailedUpdateReason


@dataclass(frozen=True)
class FailedPriceUpdateCountByReason:
    bookstore_id: int
    bookstore_name: str
    count: int
    reason: FailedUpdateReason


@dataclass(frozen=True)
class BookImportCount:
    bookstore_name: str
    count: int


@dataclass(frozen=True)
class PriceCount:
    bookstore_name: str
    count: int
