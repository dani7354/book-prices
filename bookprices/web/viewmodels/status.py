from dataclasses import dataclass


@dataclass(frozen=True)
class TimePeriodSelectOption:
    text: str
    days: int


@dataclass(frozen=True)
class IndexViewModel:
    timeperiod_options: list[TimePeriodSelectOption]


@dataclass(frozen=True)
class TableResponse:
    title: str
    columns: list[str]
    rows: list[dict[str, str]]


@dataclass(frozen=True)
class FailedPriceUpdatesResponse:
    translations: dict[str, str]
    table: TableResponse
