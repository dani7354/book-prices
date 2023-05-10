from datetime import date

from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.bookprice import BookPrice
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore, BookStoreBookPrice


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

    def delete_prices_older_than(self, earliest_date: date):
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("DELETE FROM BookPrice "
                         "WHERE Created < %s")
                cursor.execute(query, (str(earliest_date),))
                con.commit()

    def get_latest_prices(self, book_id: int) -> list:
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

    def get_book_prices_for_store(self, book: Book, book_store: BookStore) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT MAX(Id) as Id, MAX(Price) as Price, DATE(Created) as Created "
                         "FROM BookPrice bp "
                         "WHERE bp.BookId = %s AND bp.BookStoreId = %s "
                         "GROUP BY DATE(Created) "
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