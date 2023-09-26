from bookprices.web.plot.price import LineData
from bookprices.shared.db.bookprice import BookPrice
from bookprices.shared.db.bookstore import BookStore
from bookprices.web.viewmodels.price import PricesForBookInStoreResponse


DATE_FORMAT = "%d-%m-%Y"
PRICE_DECIMAL_FORMAT = ".2f"


def map_to_linedata(bookprices: list[BookPrice], bookstore: str) -> LineData:
    dates, prices = [], []
    for bp in bookprices:
        dates.append(bp.created)
        prices.append(bp.price)

    return LineData(bookstore, dates, prices)


def map_to_linedata_list(bookprices_by_bookstore: dict[BookStore, list[BookPrice]]) -> list[LineData]:
    return [map_to_linedata(prices, bookstore.name) for bookstore, prices in bookprices_by_bookstore.items()]


def map_prices_for_book_in_store(bookprices: list[BookPrice]) -> PricesForBookInStoreResponse:
    dates, prices = [], []
    for p in bookprices:
        dates.append(f"{p.created.strftime(DATE_FORMAT)}")
        prices.append(f"{p.price:{PRICE_DECIMAL_FORMAT}}")

    return PricesForBookInStoreResponse(dates, prices)

