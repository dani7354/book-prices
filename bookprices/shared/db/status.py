from datetime import datetime
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.error import FailedUpdateReason
from bookprices.shared.model.status import FailedPriceUpdateCountByReason, BookImportCount


class StatusDb(BaseDb):
    FILTER_DATE_FORMAT = "%Y-%m-%d"

    def get_failed_price_update_count_by_reason(self, date_from: datetime) -> list[FailedPriceUpdateCountByReason]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT fpu.Reason, bs.Id as BookStoreId, MAX(bs.Name) AS BookStoreName, "
                         "COUNT(fpu.Id) AS FailedUpdateCount "
                         "FROM FailedPriceUpdate fpu "
                         "INNER JOIN BookStore bs ON bs.Id = fpu.BookStoreId "
                         "WHERE fpu.Created >= %s"
                         "GROUP BY bs.Id, fpu.Reason "
                         "ORDER BY FailedUpdateCount DESC")

                cursor.execute(query, (date_from.strftime(self.FILTER_DATE_FORMAT),))
                failed_price_update_counts = []
                for row in cursor:
                    failed_price_update_counts.append(
                        FailedPriceUpdateCountByReason(
                            bookstore_id=row["BookStoreId"],
                            bookstore_name=row["BookStoreName"],
                            count=row["FailedUpdateCount"],
                            reason=FailedUpdateReason.from_str(row["Reason"])))

                return failed_price_update_counts

    def get_book_import_count_by_bookstore(self, from_date: datetime) -> list[BookImportCount]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = (
                      "SELECT bs.Name as BookStore, COUNT(*) as ImportCount "
                      "FROM Book b "
                      "INNER JOIN BookStoreBook bsb ON b.Id = bsb.BookId "
                      "INNER JOIN BookStore bs ON bsb.BookStoreId = bs.Id "
                      "WHERE b.Created >= %s "
                      "GROUP BY bsb.BookStoreId ")

                cursor.execute(query, (from_date.strftime(self.FILTER_DATE_FORMAT),))
                book_import_counts = []
                for row in cursor:
                    book_import_counts.append(
                        BookImportCount(
                            bookstore_name=row["BookStore"],
                            count=row["ImportCount"]))

                return book_import_counts
