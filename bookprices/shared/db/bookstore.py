from typing import Optional
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.bookstore import BookStore, BookInBookStore
from bookprices.shared.model.book import Book


class BookStoreDb(BaseDb):

    def get_bookstores(self) -> list[BookStore]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "HasDynamicallyLoadedContent, IsbnCssSelector "
                         "FROM BookStore")
                cursor.execute(query)
                bookstores = []
                for row in cursor:
                    bookstores.append(BookStore(row["Id"],
                                                row["Name"],
                                                row["Url"],
                                                row["SearchUrl"],
                                                row["SearchResultCssSelector"],
                                                row["PriceCssSelector"],
                                                row["ImageCssSelector"],
                                                row["IsbnCssSelector"],
                                                row["PriceFormat"],
                                                row["HasDynamicallyLoadedContent"]))

                return bookstores

    def get_missing_bookstores(self, book_id: int) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Name, PriceCssSelector, PriceFormat, Url, "
                         "SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "HasDynamicallyLoadedContent, IsbnCssSelector "
                         "FROM BookStore "
                         "WHERE Id NOT IN (SELECT BookStoreId FROM BookStoreBook WHERE BookId = %s)")
                cursor.execute(query, (book_id,))
                bookstores = []
                for row in cursor:
                    bookstores.append(BookStore(row["Id"],
                                                row["Name"],
                                                row["Url"],
                                                row["SearchUrl"],
                                                row["SearchResultCssSelector"],
                                                row["PriceCssSelector"],
                                                row["ImageCssSelector"],
                                                row["IsbnCssSelector"],
                                                row["PriceFormat"],
                                                row["HasDynamicallyLoadedContent"]))

                return bookstores

    def create_bookstore_for_book(self, book_id: int, bookstore_id: int, url: str):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO BookStoreBook (BookId, BookStoreId, Url) "
                         "VALUES (%s, %s, %s)")
                cursor.execute(query, (book_id, bookstore_id, url))
                con.commit()

    def delete_book_from_bookstore(self, book_id: int, bookstore_id: int):
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("DELETE FROM BookStoreBook "
                         "WHERE BookId = %s AND BookStoreId = %s")
                cursor.execute(query, (book_id, bookstore_id))
                con.commit()

    def get_bookstore_for_book(self, book: Book, bookstore_id: int) -> Optional[BookInBookStore]:
        bookstores_for_book = self.get_bookstores_for_books([book])
        for bookstore_book in bookstores_for_book[book.id]:
            if bookstore_book.book_store.id == bookstore_id:
                return bookstore_book

        return None

    def get_bookstores_for_books(self, books: list) -> dict:
        book_dict = {b.id: b for b in books}
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(book_dict.keys()))
                query = ("SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " 
                         "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " 
                         "bs.PriceFormat, bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector, "
                         "bs.HasDynamicallyLoadedContent, bs.IsbnCssSelector " 
                         "FROM BookStoreBook bsb " 
                         "JOIN BookStore bs ON bs.Id = bsb.BookStoreId " 
                         f"WHERE bsb.BookId IN ({ids_format_string})")

                cursor.execute(query, tuple(book_dict.keys()))

                books_in_bookstore = {}
                bookstores = {}
                for row in cursor:
                    bookstore_id = row["BookStoreId"]
                    if bookstore_id not in bookstores:
                        self._add_bookstore_from_row(row, bookstores)

                    book_id = row["BookId"]
                    if book_id not in books_in_bookstore:
                        books_in_bookstore[book_id] = []
                    books_in_bookstore[book_id].append(BookInBookStore(book_dict[book_id],
                                                                       bookstores[bookstore_id],
                                                                       row["BookUrl"]))

        return books_in_bookstore

    @staticmethod
    def _add_bookstore_from_row(row: dict, bookstore_dict: dict):
        bookstore_id = row["BookStoreId"]
        bookstore_dict[bookstore_id] = BookStore(bookstore_id,
                                                 row["BookStoreName"],
                                                 row["BookStoreUrl"],
                                                 row["SearchUrl"],
                                                 row["SearchResultCssSelector"],
                                                 row["PriceCssSelector"],
                                                 row["ImageCssSelector"],
                                                 row["IsbnCssSelector"],
                                                 row["PriceFormat"],
                                                 row["HasDynamicallyLoadedContent"])
