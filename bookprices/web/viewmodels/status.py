from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class FailedPriceUpdateCountRow:
    book_store_name: str
    count_by_reason: dict[str, int] = field(default_factory=dict[str, int])


@dataclass(frozen=True)
class FailedPriceUpdateCountTable:
    column_names: list[str]
    rows: list[FailedPriceUpdateCountRow]
