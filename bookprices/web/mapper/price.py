from bookprices.shared.db.bookprice import BookPrice
from bookprices.shared.db.bookstore import BookStore
from bookprices.shared.model.error import FailedPriceUpdateCountByReason, FailedUpdateReason
from bookprices.web.viewmodels.price import (
    PriceHistoryResponse,
    PriceHistoryForBookStoreResponse,
    PriceHistoryForDatesResponse)
from bookprices.web.viewmodels.status import FailedPriceUpdateCountRow, FailedPriceUpdateCountTable

DATE_FORMAT = "%Y-%m-%d"
PRICE_DECIMAL_FORMAT = ".2f"


def map_prices_history(bookprices: list[BookPrice]) -> PriceHistoryResponse:
    dates, prices = [], []
    for p in bookprices:
        dates.append(f"{p.created.strftime(DATE_FORMAT)}")
        prices.append(f"{p.price:{PRICE_DECIMAL_FORMAT}}")

    return PriceHistoryResponse(dates, prices)


def map_price_history_for_stores(
        bookprices_by_bookstore: dict[BookStore, list[BookPrice]]) -> PriceHistoryForDatesResponse:
    all_dates = sorted({price.created.strftime(DATE_FORMAT) for prices in bookprices_by_bookstore.values()
                        for price in prices})
    price_history_for_stores = []
    for bookstore, prices in bookprices_by_bookstore.items():
        prices_decimal_by_date = {price.created.strftime(DATE_FORMAT): price.price for price in prices}
        price_history = [f"{price:{PRICE_DECIMAL_FORMAT}}" if (price := prices_decimal_by_date.get(date)) else None
                         for date in all_dates]
        price_history_for_stores.append(PriceHistoryForBookStoreResponse(bookstore.name, price_history))

    return PriceHistoryForDatesResponse(all_dates, price_history_for_stores)


def map_failed_price_update_counts(
        failed_update_counts: list[FailedPriceUpdateCountByReason]) -> FailedPriceUpdateCountTable:
    column_names, rows = ["Boghandel"], []
    for reason in FailedUpdateReason:
        column_names.append(reason.value)

    rows_by_bookstore = {}
    for failed_update_count in failed_update_counts:
        if row := rows_by_bookstore.get(failed_update_count.bookstore_id):
            row.count_by_reason[failed_update_count.reason.value] = failed_update_count.count
        else:
            row = FailedPriceUpdateCountRow(book_store_name=failed_update_count.bookstore_name)
            rows_by_bookstore[failed_update_count.bookstore_id] = row

    return FailedPriceUpdateCountTable(column_names=column_names, rows=list(rows_by_bookstore.values()))


