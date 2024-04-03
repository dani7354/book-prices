from bookprices.shared.model.error import FailedUpdateReason
from bookprices.shared.model.status import FailedPriceUpdateCountByReason, BookImportCount, PriceCount
from bookprices.web.viewmodels.status import FailedPriceUpdatesResponse, TableResponse, BookImportCountsResponse, \
    PriceCountsResponse

BOOKSTORE_COLUMN_NAME = "book_store"


def _get_base_translations() -> dict[str, str]:
    return {BOOKSTORE_COLUMN_NAME: "Boghandler"}


def map_failed_price_update_counts(
        failed_update_counts: list[FailedPriceUpdateCountByReason]) -> FailedPriceUpdatesResponse:
    column_names = [BOOKSTORE_COLUMN_NAME] + [reason.value for reason in FailedUpdateReason]

    rows_by_bookstore = {}
    for failed_update_count in failed_update_counts:
        if not (row_for_bookstore := rows_by_bookstore.get(failed_update_count.bookstore_id)):
            row_for_bookstore = {reason.value: "0" for reason in FailedUpdateReason}
            row_for_bookstore[BOOKSTORE_COLUMN_NAME] = failed_update_count.bookstore_name
            rows_by_bookstore[failed_update_count.bookstore_id] = row_for_bookstore
        row_for_bookstore[failed_update_count.reason.value] = str(failed_update_count.count)

    table_response = TableResponse(
        title="Fejlede prisopdateringer",
        columns=column_names,
        rows=list(rows_by_bookstore.values()))

    return FailedPriceUpdatesResponse(table=table_response, translations=_get_base_translations())


def map_book_import_counts(book_import_counts: list[BookImportCount]) -> BookImportCountsResponse:
    import_count_column_name = "import_count"

    columns = [BOOKSTORE_COLUMN_NAME, import_count_column_name]
    rows = [{BOOKSTORE_COLUMN_NAME: import_count.bookstore_name,
            import_count_column_name: str(import_count.count)} for import_count in book_import_counts]

    table_response = TableResponse(
        title="Importerede bøger",
        columns=columns,
        rows=rows)

    translations = _get_base_translations()
    translations[import_count_column_name] = "Antal"

    return BookImportCountsResponse(table=table_response, translations=translations)


def map_price_counts(price_counts: list[PriceCount]) -> PriceCountsResponse:
    price_count_column_name = "price_count"

    columns = [BOOKSTORE_COLUMN_NAME, price_count_column_name]
    rows = [{BOOKSTORE_COLUMN_NAME: price_count.bookstore_name,
            price_count_column_name: str(price_count.count)} for price_count in price_counts]

    table = TableResponse(title="Opdaterede priser", columns=columns, rows=rows)

    translations = _get_base_translations()
    translations[price_count_column_name] = "Priser"

    return PriceCountsResponse(table=table, translations=translations)
