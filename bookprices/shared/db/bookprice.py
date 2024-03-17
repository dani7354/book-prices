from datetime import date
from collections import defaultdict
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore, BookStoreBookPrice
from bookprices.shared.model.error import FailedPriceUpdate, FailedUpdateReason, FailedPriceUpdateCount, \
    FailedPriceUpdateCountByReason


class BookPriceDb(BaseDb):
    def create_prices(self, book_prices: list):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                price_rows = [(price.book.id,
                               price.book_store.id,
                               str(price.price),
                               price.created) for price in book_prices]

                query = ("INSERT INTO BookPrice (BookId, BookStoreId, Price, Created) "
                         "VALUES (%s, %s, %s, %s)")
                cursor.executemany(query, price_rows)
                con.commit()

    def create_failed_price_update(self, failed_price_update: FailedPriceUpdate):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO FailedPriceUpdate (BookId, BookStoreId, Reason, Created) "
                         "VALUES (%s, %s, %s, %s)")
                cursor.execute(query, (failed_price_update.book_id,
                                       failed_price_update.bookstore_id,
                                       failed_price_update.reason.value,
                                       failed_price_update.created))
                con.commit()

    def delete_prices_older_than(self, earliest_date: date):
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("DELETE FROM BookPrice "
                         "WHERE Created < %s")
                cursor.execute(query, (str(earliest_date),))
                con.commit()

    def delete_failed_price_updates(self, book_id: int, bookstore_id: int):
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("DELETE FROM FailedPriceUpdate "
                         "WHERE BookId = %s AND BookStoreId = %s")
                cursor.execute(query, (book_id, bookstore_id))
                con.commit()

    def get_latest_prices(self, book_id: int) -> list[BookStoreBookPrice]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("With LatestPrice as ( "
                         "SELECT MAX(bp.Id) as Id "
                         "FROM BookPrice bp "
                         "WHERE bp.BookId = %s "
                         "GROUP BY bp.BookStoreId ) "
                         " "
                         "SELECT bp.Id, bsb.BookStoreId, bs.Name as BookStoreName, CONCAT(bs.Url, bsb.Url) as Url, "
                         "bp.Price, bp.Created "
                         "FROM BookStoreBook bsb "
                         "INNER JOIN BookStore bs ON bs.Id = bsb.BookStoreId "
                         "LEFT OUTER JOIN BookPrice bp "
                         "INNER JOIN LatestPrice lp ON bp.Id = lp.Id "
                         "ON bp.BookId = bsb.BookId AND bp.BookStoreId = bsb.BookStoreId "
                         "WHERE bsb.BookId = %s "
                         "ORDER BY bp.Price ASC;")

                cursor.execute(query, (book_id, book_id))

                latest_prices_for_book = []
                for row in cursor:
                    latest_prices_for_book.append(BookStoreBookPrice(row["Id"],
                                                                     row["BookStoreId"],
                                                                     row["BookStoreName"],
                                                                     row["Url"],
                                                                     row["Price"],
                                                                     row["Created"]))
                return latest_prices_for_book

    def get_book_prices_for_store(self, book: Book, book_store: BookStore) -> list[BookPrice]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("With LatestPrices as ( "
                         "SELECT MAX(Id) as Id "
                         "FROM BookPrice bp "
                         "WHERE bp.BookId = %s AND bp.BookStoreId = %s "
                         "GROUP BY DATE(Created))"
                         " "
                         "SELECT bp.Id, bp.Price, DATE(bp.Created) as Created "
                         "FROM BookPrice bp "
                         "INNER JOIN LatestPrices lp ON bp.Id = lp.Id "
                         "ORDER BY Created DESC;")

                cursor.execute(query, (book.id, book_store.id))

                book_prices_for_store = []
                for row in cursor:
                    book_prices_for_store.append(BookPrice(row["Id"],
                                                           book,
                                                           book_store,
                                                           row["Price"],
                                                           row["Created"]))
                return book_prices_for_store

    def get_all_book_prices(self, book: Book) -> dict[BookStore, list[BookPrice]]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("With LatestPrices as ( "
                         "SELECT MAX(Id) as Id "
                         "FROM BookPrice bp "
                         "WHERE bp.BookId = %s "
                         "GROUP BY DATE(Created), bp.BookStoreId)"
                         " "
                         "SELECT bp.Id, bp.BookStoreId, bp.Price, DATE(bp.Created) as Created "
                         "FROM BookPrice bp "
                         "INNER JOIN LatestPrices lp ON bp.Id = lp.Id "
                         "ORDER BY Created DESC;")

                cursor.execute(query, (book.id,))
                bookstores = {}
                prices_by_bookstores: defaultdict[BookStore, list[BookPrice]] = defaultdict(list)
                for row in cursor:
                    bookstore_id = row["BookStoreId"]
                    bookstore = bookstores.get(bookstore_id)
                    if not bookstore:
                        bookstore = self.get_book_store(bookstore_id)
                        bookstores[bookstore_id] = bookstore

                    prices_by_bookstores[bookstore].append(BookPrice(row["Id"],
                                                                     book,
                                                                     bookstore,
                                                                     row["Price"],
                                                                     row["Created"]))
                return prices_by_bookstores

    def get_book_ids_with_oldest_prices(self, limit: int) -> set[int]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT bsb.BookId, bsb.BookStoreId, MAX(bp.Created) as Created "
                         "FROM BookStoreBook bsb "
                         "LEFT JOIN BookPrice bp ON bp.BookId = bsb.BookId AND bp.BookStoreId = bsb.BookStoreId "
                         "GROUP BY BookId, BookStoreId "
                         "ORDER BY Created "
                         "LIMIT %s;")

                cursor.execute(query, (limit,))
                book_ids = set()
                for row in cursor:
                    book_ids.add(row["BookId"])

                return book_ids

    def get_failed_price_update_counts(self) -> list[FailedPriceUpdateCount]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT BookId, BookStoreId, COUNT(*) AS Count "
                         "FROM FailedPriceUpdate "
                         "GROUP BY BookId, BookStoreId;")

                cursor.execute(query)
                failed_price_update_counts = []
                for row in cursor:
                    book_id = row["BookId"]
                    bookstore_id = row["BookStoreId"]
                    count = row["Count"]

                    failed_price_update_counts.append(FailedPriceUpdateCount(book_id, bookstore_id, count))

                return failed_price_update_counts

    def get_latest_failed_price_updates(self, book_id: int, bookstore_id: int, limit: int) -> list[FailedPriceUpdate]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, BookId, BookStoreId, Reason, Created "
                         "FROM FailedPriceUpdate "
                         "WHERE BookId = %s AND BookStoreId = %s "
                         "ORDER BY Created DESC "
                         "LIMIT %s;")

                cursor.execute(query, (book_id, bookstore_id, limit))
                failed_price_updates = []
                for row in cursor:
                    failed_price_updates.append(
                        FailedPriceUpdate(row["Id"],
                                          row["BookId"],
                                          row["BookStoreId"],
                                          FailedUpdateReason.from_str(row["Reason"]),
                                          row["Created"]))

                return failed_price_updates

    def get_failed_price_update_count_by_reason(self) -> list[FailedPriceUpdateCountByReason]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT fpu.Reason, bs.Id as BookStoreId, MAX(bs.Name) AS BookStoreName, "
                         "COUNT(fpu.Id) AS FailedUpdateCount "
                         "FROM FailedPriceUpdate fpu "
                         "INNER JOIN BookStore bs ON bs.Id = fpu.BookStoreId "
                         "GROUP BY bs.Id, fpu.Reason "
                         "ORDER BY FailedUpdateCount DESC")

                cursor.execute(query)
                failed_price_update_counts = []
                for row in cursor:
                    failed_price_update_counts.append(
                        FailedPriceUpdateCountByReason(
                            bookstore_id=row["BookStoreId"],
                            bookstore_name=row["BookStoreName"],
                            count=row["FailedUpdateCount"],
                            reason=FailedUpdateReason.from_str(row["Reason"])))

                return failed_price_update_counts
