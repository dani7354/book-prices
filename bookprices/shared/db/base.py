from mysql.connector import connection
from bookprices.shared.model.bookstore import BookStore


class BaseDb:
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_name: str):
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

    def get_book_store(self, book_store_id: int) -> BookStore:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name,  PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, PriceCssSelector, ImageCssSelector, "
                         "HasDynamicallyLoadedContent, IsbnCssSelector "
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
                                                 row["IsbnCssSelector"],
                                                 row["PriceFormat"],
                                                 row["HasDynamicallyLoadedContent"],
                                                 row["ColorHex"]))

                return book_stores[0] if len(book_stores) > 0 else None
