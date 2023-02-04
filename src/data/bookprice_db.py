from mysql.connector import (connection)
from .model import Book, BookStore, BookInBookStore, BookStoreSitemap, BookStoreBookPrice


class BookPriceDb:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port,
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

    def get_connection(self) -> connection:
        con = connection.MySQLConnection(host=self.db_host,
                                         user=self.db_user,
                                         password=self.db_password,
                                         database=self.db_name)
        return con

    def get_books(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Title, Author "
                         "FROM Book "
                         "ORDER BY Title ASC;")
                cursor.execute(query)
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Title"], row["Author"])
                    books.append(book)

                return books

    def get_book(self, id) -> Book:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Title, Author "
                         "FROM Book "
                         "WHERE Id = %s;")
                cursor.execute(query, (id, ))
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Title"], row["Author"])
                    books.append(book)

                return books[0] if len(books) > 0 else None

    def get_book_stores_for_books(self, books) -> dict:
        book_dict = {b.id: b for b in books}
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(book_dict.keys()))
                query = "SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " \
                        "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " \
                        "bs.PriceFormat " \
                        "FROM BookStoreBook bsb " \
                        "JOIN BookStore bs ON bs.Id = bsb.BookStoreId " \
                        f"WHERE bsb.BookId IN ({ids_format_string})"

                cursor.execute(query, tuple(book_dict.keys()))

                books_in_bookstore = {}
                book_stores = {}
                for row in cursor:
                    book_store_id = row["BookStoreId"]
                    if book_store_id not in book_stores:
                        self._add_book_store_from_row(row, book_stores)

                    book_id = row["BookId"]
                    if book_id not in books_in_bookstore:
                        books_in_bookstore[book_id] = []
                    books_in_bookstore[book_id].append(BookInBookStore(book_dict[book_id],
                                                                       book_stores[book_store_id],
                                                                       row["BookUrl"]))

        return books_in_bookstore

    def create_prices(self, book_prices):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                price_rows = [(price.book.id, price.book_store.id, str(price.price), price.created) for price in book_prices]

                query = ("INSERT INTO BookPrice (BookId, BookStoreId, Price, Created) " 
                         "VALUES (%s, %s, %s, %s)")
                cursor.executemany(query, price_rows)
                con.commit()

    def get_latest_prices(self, book_id) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT bp.Id, bp.BookStoreId, bs.Name as BookStoreName, CONCAT(bs.Url, bsb.Url) as Url, "
                         "bp.Price, bp.Created "
                         "FROM BookPrice bp "
                         "INNER JOIN BookStore bs ON bs.Id = bp.BookStoreId "
                         "INNER JOIN BookStoreBook bsb ON bsb.BookId = bp.BookId AND bsb.BookStoreId = bp.BookStoreId "
                         "WHERE bp.BookId = %s AND bp.Created IN "
                         "(SELECT MAX(bp2.Created) "
                         "FROM BookPrice bp2 "
                         "WHERE bp2.BookId = bp.BookId AND bp2.BookStoreId = bp.BookStoreId) "
                         "ORDER BY Price ASC;")

                cursor.execute(query, (book_id,))

                latest_prices_for_book = []
                for row in cursor:
                    latest_prices_for_book.append(BookStoreBookPrice(row["Id"],
                                                                     row["BookStoreId"],
                                                                     row["BookStoreName"],
                                                                     row["Url"],
                                                                     row["Price"],
                                                                     row["Created"]))
                return latest_prices_for_book

    def get_sitemaps(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT bss.Id as SitemapId, bss.Url as SitemapUrl, bs.Id as BookStoreId, "
                         "bs.Url as BookStoreUrl, bs.Name as BookStoreName, bs.PriceCssSelector, bs.PriceFormat " 
                         "FROM BookStoreSitemap bss "
                         "INNER JOIN BookStore bs ON bs.Id = bss.BookStoreId;")

                cursor.execute(query)

                book_stores = {}
                sitemaps = []
                for row in cursor:
                    book_store_id = row["BookStoreId"]
                    if book_store_id not in book_stores:
                        self._add_book_store_from_row(row, book_stores)

                    sitemaps.append(BookStoreSitemap(row["SitemapId"], row["SitemapUrl"], book_stores[book_store_id]))

        return sitemaps

    @staticmethod
    def _add_book_store_from_row(row, book_store_dict):
        book_store_id = row["BookStoreId"]
        book_store_dict[book_store_id] = BookStore(book_store_id,
                                                   row["BookStoreName"],
                                                   row["BookStoreUrl"],
                                                   row["PriceCssSelector"],
                                                   row["PriceFormat"])
