from collections import defaultdict
from enum import StrEnum

from flask_caching import Cache
from datetime import timedelta, datetime
from bookprices.shared.cache.key_generator import (
    get_failed_count_by_reason_key, get_book_import_count_key, get_price_count_key, get_price_count_by_bookstore_key,
    get_job_run_statistics_key)
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.job_service import JobService, JobRunStatisticsSchemaFields
from bookprices.web.shared.enum import CacheTtlOption
from bookprices.web.viewmodels.status import (
    TimePeriodSelectOption, UpdatedPricesForBookStoreResponse, TableResponse, PriceCountsResponse,
    BookImportCountsResponse, FailedPriceUpdatesResponse, JobRunStatisticsResponse)


class TableColumn(StrEnum):
    BOOK_STORE = "book_store"
    BOOK_COUNT = "book_count"
    UPDATED_PRICES = "updated_prices"
    UPDATED_PERCENTAGE = "updated_percentage"
    PRICE_COUNT = "price_count"
    JOB_NAME = "job_name"
    TOTAL_JOB_RUN_COUNT = "job_run_count"


class StatusService:
    """ Service for getting status information for the site dashboard. """

    def __init__(self, unit_of_work: UnitOfWork, job_service: JobService,  cache: Cache) -> None:
        self._unit_of_work = unit_of_work
        self._job_service = job_service
        self._cache = cache
        self._translations: dict[str, str] = {
            TableColumn.BOOK_STORE: "Boghandler",
            TableColumn.PRICE_COUNT: "Priser",
            TableColumn.BOOK_COUNT: "Bøger",
            TableColumn.UPDATED_PRICES: "Prisopdateringer",
            TableColumn.UPDATED_PERCENTAGE: "Opdateringsprocent",
            TableColumn.JOB_NAME: "Job",
            TableColumn.TOTAL_JOB_RUN_COUNT: "Total",
        }

    def get_failed_price_updates_by_bookstore(self, days: int) -> FailedPriceUpdatesResponse:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_failed_count_by_reason_key(date_from)
        failed_update_counts = []
        if cached_failed_counts := self._cache.get(cache_key):
            failed_update_counts = cached_failed_counts
        else:
            with self._unit_of_work as uow:
                if source_failed_count := uow.failed_price_update_repository.get_failed_update_count_by_reason(date_from):
                    self._cache.set(
                        get_failed_count_by_reason_key(date_from), source_failed_count, timeout=CacheTtlOption.SHORT.value)
                    failed_update_counts = source_failed_count

        return self._create_failed_price_updates_response(failed_update_counts)

    def _create_failed_price_updates_response(self, failed_price_updates: list[tuple[str, int]]) -> FailedPriceUpdatesResponse:
        unique_columns = {str(TableColumn.BOOK_STORE)}
        rows_by_bookstore_id = defaultdict(dict)
        for bookstore_id, bookstore_name, reason, count in failed_price_updates:
            rows_by_bookstore_id[bookstore_id][TableColumn.BOOK_STORE] = bookstore_name
            if reason:
                rows_by_bookstore_id[bookstore_id][reason] = count
                unique_columns.add(reason)

        for row in rows_by_bookstore_id.values():
            for column in unique_columns:
                if column not in row:
                    row[column] = 0

        rows = list(rows_by_bookstore_id.values())
        columns = sorted(unique_columns, reverse=True)
        translations = self._get_translations_for_columns(columns)
        table_response = TableResponse(title="Fejlede prisopdateringer", columns=columns, rows=rows)

        return FailedPriceUpdatesResponse(table=table_response, translations=translations)

    def get_book_import_count_by_bookstore(self, days: int) -> BookImportCountsResponse:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_book_import_count_key(date_from)
        import_counts = []
        if cached_import_counts := self._cache.get(cache_key):
            import_counts = cached_import_counts
        else:
            with self._unit_of_work as uow:
                if source_import_counts := uow.bookstore_repository.get_book_import_count_by_bookstore(date_from):
                    self._cache.set(cache_key, source_import_counts, timeout=CacheTtlOption.SHORT.value)
                    import_counts = source_import_counts

        return self._create_book_import_count_response(import_counts)

    def get_job_run_statistics_by_job(self, days: int) -> JobRunStatisticsResponse:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_job_run_statistics_key(date_from)
        if cached_job_run_stats := self._cache.get(cache_key):
            job_run_stats = cached_job_run_stats
        else:

            job_run_stats_source = self._job_service.get_finished_job_runs_statistics(days)
            self._cache.set(cache_key, job_run_stats_source, timeout=CacheTtlOption.SHORT.value)
            job_run_stats = job_run_stats_source

        return self._create_job_run_statistics_response(job_run_stats)

    def _create_book_import_count_response(self, import_counts: list[tuple[int, str, int]]) -> BookImportCountsResponse:
        rows = [{TableColumn.BOOK_STORE: bookstore_name, TableColumn.BOOK_COUNT: str(count)}
                for _, bookstore_name, count in import_counts]

        columns = list(rows[0].keys() if rows else [])
        translations = self._get_translations_for_columns(columns)
        table = TableResponse(title="Importerede bøger", columns=columns, rows=rows)

        return BookImportCountsResponse(table=table, translations=translations)

    def get_price_count_by_bookstore(self, days: int) -> PriceCountsResponse:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_price_count_key(date_from)
        price_counts = []
        if cached_price_counts := self._cache.get(cache_key):
            price_counts = cached_price_counts
        else:
            with self._unit_of_work as uow:
                if source_price_counts := uow.bookprice_repository.get_price_count_by_bookstore(date_from):
                    self._cache.set(cache_key, source_price_counts, timeout=CacheTtlOption.SHORT.value)
                    price_counts = source_price_counts

        return self._create_price_count_by_bookstore_response(price_counts)

    def _create_price_count_by_bookstore_response(self, price_counts: list[tuple[int, str, int]]) -> PriceCountsResponse:
        rows = []
        for bookstore_id, bookstore_name, count in price_counts:
            rows.append({
                TableColumn.BOOK_STORE: bookstore_name,
                TableColumn.PRICE_COUNT: str(count)})

        columns = list(rows[0].keys() if rows else [])
        translations = self._get_translations_for_columns(columns)
        table = TableResponse(title="Opdaterede priser", columns=columns, rows=rows)

        return PriceCountsResponse(table=table, translations=translations)

    def get_updated_prices_for_bookstores(self, days: int) -> UpdatedPricesForBookStoreResponse:
        date_from = datetime.now() - timedelta(days=days)
        cache_key = get_price_count_by_bookstore_key(date_from)
        price_counts_for_bookstore = []
        if cached_price_counts_for_bookstore := self._cache.get(cache_key):
            price_counts_for_bookstore = cached_price_counts_for_bookstore
        else:
            with self._unit_of_work as uow:
                if (source_price_counts_for_bookstore := uow.
                        bookstore_repository.get_bookstores_with_updated_prices_percentage(date_from)):
                    self._cache.set(cache_key, source_price_counts_for_bookstore, timeout=CacheTtlOption.SHORT.value)
                    price_counts_for_bookstore = source_price_counts_for_bookstore

        return self._create_updated_prices_for_bookstore_response(price_counts_for_bookstore)

    def _create_updated_prices_for_bookstore_response(
            self,
            updated_prices_for_bookstore: list[tuple[int, str, int, int, float]]) -> UpdatedPricesForBookStoreResponse:
        rows = []
        for bookstore_id, bookstore_name, book_count, updated_prices_count, updated_percentage in updated_prices_for_bookstore:
            rows.append({
                TableColumn.BOOK_STORE: bookstore_name,
                TableColumn.BOOK_COUNT: book_count,
                TableColumn.UPDATED_PRICES: updated_prices_count,
                TableColumn.UPDATED_PERCENTAGE: f"{updated_percentage:.2f}%"
            })

        columns = list(rows[0].keys() if rows else [])
        translations = self._get_translations_for_columns(columns)
        table_response = TableResponse(title="Prisopdateringer for boghandlere", columns=columns, rows=rows)

        return UpdatedPricesForBookStoreResponse(translations=translations, table=table_response)

    def _create_job_run_statistics_response(self, json: dict) -> JobRunStatisticsResponse:
        rows = []
        unique_statuses = set()
        for job_run in json[JobRunStatisticsSchemaFields.JOB_RUNS]:
            row = {
                TableColumn.JOB_NAME: job_run[JobRunStatisticsSchemaFields.JOB_NAME],
                TableColumn.TOTAL_JOB_RUN_COUNT: job_run[JobRunStatisticsSchemaFields.TOTAL_JOB_RUN_COUNT]
            }

            job_run_percentage = job_run[JobRunStatisticsSchemaFields.PERCENTAGE_BY_STATUS]
            for status, count in job_run[JobRunStatisticsSchemaFields.COUNT_BY_STATUS].items():
                unique_statuses.add(status)
                percentage = job_run_percentage[status]
                row[status] = self._format_count_percentage_cell(count, percentage)

            for status in unique_statuses:
                if status not in row:
                    row[status] = self._format_count_percentage_cell(0, 0.00)

            rows.append(row)

        rows.sort(key=lambda x: x[TableColumn.TOTAL_JOB_RUN_COUNT], reverse=True)
        columns = list(rows[0].keys() if rows else [])
        translations = self._get_translations_for_columns(columns)
        table_response = TableResponse(title="Jobkørsler", columns=columns, rows=rows)

        return JobRunStatisticsResponse(translations=translations, table=table_response)

    def _get_translations_for_columns(self, columns: list[str]) -> dict[str, str]:
        return {column: self._translations.get(column, column) for column in columns}

    @staticmethod
    def get_timeperiod_options() -> list[TimePeriodSelectOption]:
        timeperiod_options = [
            TimePeriodSelectOption(text="1 dag", days=1),
            TimePeriodSelectOption(text="7 dage", days=7),
            TimePeriodSelectOption(text="14 dage", days=14),
            TimePeriodSelectOption(text="30 dage", days=30),
            TimePeriodSelectOption(text="90 dage", days=90),
            TimePeriodSelectOption(text="365 dage", days=365),
        ]

        return timeperiod_options

    @staticmethod
    def _format_count_percentage_cell(count: int, percentage: float) -> str:
        return f"{count} ({percentage:.2f}%)"