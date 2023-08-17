from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.bookstore import BookStore, BookInBookStore
from bookprices.shared.model.book import Book


class BookStoreDb(BaseDb):

    def get_book_stores(self) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "HasDynamicallyLoadedContent "
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
                                                 row["PriceFormat"],
                                                 row["HasDynamicallyLoadedContent"]))

                return book_stores

    def get_missing_book_stores(self, book_id: int) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "HasDynamicallyLoadedContent "
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
                                                 row["PriceFormat"],
                                                 row["HasDynamicallyLoadedContent"]))

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
                query = ("SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " 
                         "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " 
                         "bs.PriceFormat, bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector, "
                         "bs.HasDynamicallyLoadedContent " 
                         "FROM BookStoreBook bsb " 
                         "JOIN BookStore bs ON bs.Id = bsb.BookStoreId " 
                         f"WHERE bsb.BookId IN ({ids_format_string})")

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
                                                   row["PriceFormat"],
                                                   row["HasDynamicallyLoadedContent"])
