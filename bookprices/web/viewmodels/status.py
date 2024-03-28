from dataclasses import dataclass, field
from typing import ClassVar

from bookprices.shared.model.error import FailedUpdateReason


@dataclass(frozen=True)
class FailedPriceUpdateCountRow:
    book_store_name: str
    count_by_reason: dict[str, int] = field(default_factory=lambda: {reason.value: 0 for reason in FailedUpdateReason})


@dataclass(frozen=True)
class FailedPriceUpdateCountTable:
    column_names: list[str]
    rows: list[FailedPriceUpdateCountRow]
