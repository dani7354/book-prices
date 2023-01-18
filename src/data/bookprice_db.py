from mysql.connector import (connection)
from .model import Book, BookStore, BookInBookStore


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
                         "FROM Book;")
                cursor.execute(query)
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Title"], row["Author"])
                    books.append(book)

                return books

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
                        book_stores[book_store_id] = BookStore(book_store_id,
                                                               row["BookStoreName"],
                                                               row["BookStoreUrl"],
                                                               row["PriceCssSelector"],
                                                               row["PriceFormat"])

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
