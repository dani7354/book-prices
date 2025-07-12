from dataclasses import dataclass


@dataclass(frozen=True)
class PriceHistoryResponse:
    dates: list[str]
    prices: list[str]
    row_css_classes: list[str]


@dataclass(frozen=True)
class PriceHistoryForBookStoreResponse:
    bookstore_name: str
    color: str
    prices: list[str]


@dataclass(frozen=True)
class PriceHistoryForDatesResponse:
    dates: list[str]
    prices: list[PriceHistoryForBookStoreResponse]
