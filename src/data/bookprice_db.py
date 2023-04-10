from mysql.connector import connection
from datetime import date
from .model import Book, BookStore, BookInBookStore, BookStoreSitemap, BookStoreBookPrice, BookPrice


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

    def create_book(self, book: Book) -> int:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = "INSERT INTO Book(Isbn, Title, Author) VALUES (%s, %s, %s);"
                cursor.execute(query, (book.isbn, book.title, book.author))
                con.commit()

                query = "SELECT LAST_INSERT_ID() as Id;"
                cursor.execute(query)

                for row in cursor:
                    if "Id" in row:
                        return row["Id"]

                return -1

    def update_book(self, book: Book):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE Book "
                         "SET Title = %s, Author = %s, ImageUrl = %s "
                         "WHERE Id = %s;")
                cursor.execute(query, (book.title, book.author, book.image_url, book.id))
                con.commit()

    def get_books(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, ImageUrl "
                         "FROM Book "
                         "ORDER BY Title ASC;")
                cursor.execute(query)
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Isbn"], row["Title"], row["Author"], row["ImageUrl"])
                    books.append(book)

                return books

    def search_books(self, search_phrase: str) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                phrase_with_wildcards = f"{search_phrase}%"
                query = ("SELECT Id, Isbn, Title, Author, ImageUrl "
                         "FROM Book "
                         "WHERE Title LIKE %s OR Author LIKE %s "
                         "ORDER BY Title ASC;")
                cursor.execute(query, (phrase_with_wildcards, phrase_with_wildcards))
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Isbn"], row["Title"], row["Author"], row["ImageUrl"])
                    books.append(book)

                return books

    def get_book(self, book_id: int) -> Book:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, ImageUrl "
                         "FROM Book "
                         "WHERE Id = %s;")
                cursor.execute(query, (book_id,))
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Isbn"], row["Title"], row["Author"], row["ImageUrl"])
                    books.append(book)

                return books[0] if len(books) > 0 else None

    def get_book_by_isbn(self, book_id: str) -> Book:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, ImageUrl "
                         "FROM Book "
                         "WHERE Isbn = %s;")
                cursor.execute(query, (book_id,))
                books = []
                for row in cursor:
                    book = Book(row["Id"], row["Isbn"], row["Title"], row["Author"], row["ImageUrl"])
                    books.append(book)

                return books[0] if len(books) > 0 else None

    def get_book_store(self, book_store_id: int) -> BookStore:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name,  PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, PriceCssSelector, ImageCssSelector "
                         "FROM BookStore "
                         "WHERE Id = %s;")
                cursor.execute(query, (book_store_id,))
                book_stores = []
                for row in cursor:
                    book_stores.append(BookStore(row["Id"],
                                                 row["Name"],
                                                 row["Url"],
                                                 row["SearchUrl"],
                                                 row["SearchResultCssSelector"],
                                                 row["PriceCssSelector"],
                                                 row["ImageCssSelector"],
                                                 row["PriceFormat"]))

                return book_stores[0] if len(book_stores) > 0 else None

    def get_book_stores(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector "
                         "FROM BookStore")
                cursor.execute(query)
                book_stores = []
                for row in cursor:
                    book_stores.append(BookStore(row["Id"],
                                                 row["Name"],
                                                 row["Url"],
                                                 row["SearchUrl"],
                                                 row["SearchResultCssSelector"],
                                                 row["PriceCssSelector"],
                                                 row["ImageCssSelector"],
                                                 row["PriceFormat"]))

                return book_stores

    def get_missing_book_stores(self, book_id: int) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector "
                         "FROM BookStore "
                         "WHERE Id NOT IN (SELECT BookStoreId FROM BookStoreBook WHERE BookId = %s)")
                cursor.execute(query, (book_id,))
                book_stores = []
                for row in cursor:
                    book_stores.append(BookStore(row["Id"],
                                                 row["Name"],
                                                 row["Url"],
                                                 row["SearchUrl"],
                                                 row["SearchResultCssSelector"],
                                                 row["PriceCssSelector"],
                                                 row["ImageCssSelector"],
                                                 row["PriceFormat"]))

                return book_stores

    def create_book_store_for_book(self, book_id: int, book_store_id: int, url: str):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO BookStoreBook (BookId, BookStoreId, Url) "
                         "VALUES (%s, %s, %s)")
                cursor.execute(query, (book_id, book_store_id, url))
                con.commit()

    def get_book_store_for_book(self, book: Book, book_store_id: int):
        book_stores_for_book = self.get_book_stores_for_books([book])
        for book_store_book in book_stores_for_book[book.id]:
            if book_store_book.book_store.id == book_store_id:
                return book_store_book

        return None

    def get_book_stores_for_books(self, books: list) -> dict:
        book_dict = {b.id: b for b in books}
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(book_dict.keys()))
                query = "SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " \
                        "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " \
                        "bs.PriceFormat, bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector " \
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

    def get_sitemaps(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT bss.Id as SitemapId, bss.Url as SitemapUrl, bs.Id as BookStoreId, "
                         "bs.Url as BookStoreUrl, bs.Name as BookStoreName, bs.PriceCssSelector, bs.PriceFormat, "
                         "bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector " 
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
    def _add_book_store_from_row(row: dict, book_store_dict: dict):
        book_store_id = row["BookStoreId"]
        book_store_dict[book_store_id] = BookStore(book_store_id,
                                                   row["BookStoreName"],
                                                   row["BookStoreUrl"],
                                                   row["SearchUrl"],
                                                   row["SearchResultCssSelector"],
                                                   row["PriceCssSelector"],
                                                   row["ImageCssSelector"],
                                                   row["PriceFormat"])
