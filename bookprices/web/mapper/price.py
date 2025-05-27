from bookprices.shared.db.bookprice import BookPrice
from bookprices.shared.db.bookstore import BookStore
from bookprices.web.viewmodels.price import (
    PriceHistoryResponse,
    PriceHistoryForBookStoreResponse,
    PriceHistoryForDatesResponse)


DATE_FORMAT = "%Y-%m-%d"
PRICE_DECIMAL_FORMAT = ".2f"

GREEN_ROW_CSS_CLASS = "table-success"
RED_ROW_CSS_CLASS = "table-danger"
YELLOW_ROW_CSS_CLASS = "table-warning"


def _get_css_classes_for_price_rows(prices: list[BookPrice]) -> list[str]:
    min_price = min(prices, key=lambda p: p.price).price
    max_price = max(prices, key=lambda p: p.price).price
    min_max_diff = max_price - min_price
    price_diff_margin = min_max_diff * 0.1

    css_classes = []
    for bp in prices:
        if bp.price <= min_price + price_diff_margin < max_price - price_diff_margin:
            css_classes.append(GREEN_ROW_CSS_CLASS)
        elif bp.price >= max_price - price_diff_margin > min_price + price_diff_margin:
            css_classes.append(RED_ROW_CSS_CLASS)
        elif bp.price > min_price + price_diff_margin < max_price - price_diff_margin:
            css_classes.append(YELLOW_ROW_CSS_CLASS)
        else:
            css_classes.append("")

    return css_classes


def map_prices_history(bookprices: list[BookPrice]) -> PriceHistoryResponse:
    dates, prices = [], []
    for p in bookprices:
        dates.append(f"{p.created.strftime(DATE_FORMAT)}")
        prices.append(f"{p.price:{PRICE_DECIMAL_FORMAT}}")
    row_css_classes = _get_css_classes_for_price_rows(bookprices)

    return PriceHistoryResponse(dates, prices, row_css_classes)


def _get_price_history_for_all_dates(all_dates: list[str], prices_for_bookstore: list[BookPrice]) -> list[str]:
    prices_decimal_by_date = {price.created.strftime(DATE_FORMAT): price.price for price in prices_for_bookstore}
    prices_history = []
    last_price = None
    for date in all_dates:
        if price := prices_decimal_by_date.get(date):
            last_price = price
        else:
            price = last_price

        formatted_price = f"{price:{PRICE_DECIMAL_FORMAT}}" if price else None
        prices_history.append(formatted_price)

    return prices_history


def map_price_history_for_stores(
        bookprices_by_bookstore: dict[BookStore, list[BookPrice]]) -> PriceHistoryForDatesResponse:
    all_dates = sorted({price.created.strftime(DATE_FORMAT) for prices in bookprices_by_bookstore.values()
                        for price in prices})
    price_history_for_stores = [
        PriceHistoryForBookStoreResponse(bookstore.name, _get_price_history_for_all_dates(all_dates, prices))
        for bookstore, prices in bookprices_by_bookstore.items()
    ]

    return PriceHistoryForDatesResponse(all_dates, price_history_for_stores)
