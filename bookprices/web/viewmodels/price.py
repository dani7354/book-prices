from dataclasses import dataclass


@dataclass(frozen=True)
class PricesForBookInStoreResponse:
    dates: list[str]
    prices: list[str]
