from bookprices.web.plot.price import LineData
from bookprices.shared.db.bookprice import BookPrice
from bookprices.shared.db.bookstore import BookStore


def map_to_linedata(bookprices: list[BookPrice], bookstore: str) -> LineData:
    dates, prices = [], []
    for bp in bookprices:
        dates.append(bp.created)
        prices.append(bp.price)

    return LineData(bookstore, dates, prices)


def map_to_linedata_list(bookprices_by_bookstore: dict[BookStore, list[BookPrice]]) -> list[LineData]:
    return [map_to_linedata(prices, bookstore.name) for bookstore, prices in bookprices_by_bookstore.items()]
