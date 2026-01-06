from collections import defaultdict
from typing import Optional, Any
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.bookstore import BookStore, BookInBookStore
from bookprices.shared.model.book import Book


class BookStoreDb(BaseDb):

    def get_bookstores(self) -> list[BookStore]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id as BookStoreId, Name as BookStoreName, PriceCssSelector, PriceFormat, "
                         "Url as BookStoreUrl, SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "IsbnCssSelector, ColorHex, ScraperId"
                         "FROM BookStore "
                         "ORDER BY Id ASC")
                cursor.execute(query)

                return [self._map_bookstore(row) for row in cursor]

    def get_bookstore(self, bookstore_id: int) -> BookStore | None:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id as BookStoreId, Name as BookStoreName, PriceCssSelector, PriceFormat, "
                         "Url as BookStoreUrl, SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "IsbnCssSelector, ColorHex, ScraperId "
                         "FROM BookStore "
                         "WHERE Id = %s")
                cursor.execute(query, (bookstore_id,))

                return self._map_bookstore(row) if (row := cursor.fetchone()) else None

    def create_bookstore(self, bookstore: BookStore) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO BookStore (Name, Url, SearchUrl, "
                         "SearchResultCssSelector, PriceCssSelector, "
                         "ImageCssSelector, IsbnCssSelector, PriceFormat, "
                         "ColorHex, ScraperId) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(query, (bookstore.name,
                                       bookstore.url,
                                       bookstore.search_url,
                                       bookstore.search_result_css_selector,
                                       bookstore.price_css_selector,
                                       bookstore.image_css_selector,
                                       bookstore.isbn_css_selector,
                                       bookstore.price_format,
                                       bookstore.color_hex,
                                       bookstore.scraper_id))
                con.commit()

    def update_bookstore(self, bookstore: BookStore) -> BookStore:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("UPDATE BookStore "
                         "SET Name = %s, Url = %s, SearchUrl = %s, "
                         "SearchResultCssSelector = %s, PriceCssSelector = %s, "
                         "ImageCssSelector = %s, IsbnCssSelector = %s, "
                         "PriceFormat = %s, ScraperId = %s, "
                         "ColorHex = %s "
                         "WHERE Id = %s")
                cursor.execute(query, (bookstore.name,
                                       bookstore.url,
                                       bookstore.search_url,
                                       bookstore.search_result_css_selector,
                                       bookstore.price_css_selector,
                                       bookstore.image_css_selector,
                                       bookstore.isbn_css_selector,
                                       bookstore.price_format,
                                       bookstore.scraper_id,
                                       bookstore.color_hex,
                                       bookstore.id))
                con.commit()

                return self.get_bookstore(bookstore.id)

    def delete_bookstore(self, bookstore_id: int) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = "DELETE FROM BookStore WHERE Id = %s"
                cursor.execute(query, (bookstore_id,))
                con.commit()

    def get_missing_bookstores(self, book_id: int) -> list:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id as BookStoreId, Name as BookStoreName, PriceCssSelector, PriceFormat, "
                         "Url as BookStoreUrl, SearchUrl, SearchResultCssSelector, ImageCssSelector, "
                         "IsbnCssSelector, ColorHex, ScraperId "
                         "FROM BookStore "
                         "WHERE Id NOT IN (SELECT BookStoreId FROM BookStoreBook WHERE BookId = %s)")
                cursor.execute(query, (book_id,))

                return [self._map_bookstore(row) for row in cursor]

    def get_book_isbn_and_missing_bookstores(self, offset: int, limit: int) -> list[dict[str, Any]]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT b.Id as BookId, b.Isbn, bs.Id as BookStoreId, bs.SearchUrl, bs.SearchResultCssSelector, "
                         "bs.IsbnCssSelector, bs.Url, bs.ColorHex, bs.ScraperId "
                         "FROM Book b "
                         "CROSS JOIN BookStore bs "
                         "LEFT JOIN BookStoreBook bsb ON bsb.BookId = b.Id AND bsb.BookStoreId = bs.Id "
                         "WHERE bsb.BookId IS NULL AND bsb.BookStoreId IS NULL AND bs.SearchUrl IS NOT NULL "
                         "ORDER BY b.Id DESC "
                         "LIMIT %s OFFSET %s;")

                cursor.execute(query, (limit, offset))

                return cursor.fetchall()

    def create_bookstores_for_books(self, bookstores_for_books: list[tuple[int, int, str]]) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT INTO BookStoreBook (BookId, BookStoreId, Url) "
                         "VALUES (%s, %s, %s)")
                cursor.executemany(query, bookstores_for_books)
                con.commit()

    def create_bookstore_for_book_if_not_exists(self, book_id: int, bookstore_id: int, url: str) -> None:
        with self.get_connection() as con:
            with con.cursor() as cursor:
                query = ("INSERT IGNORE INTO BookStoreBook (BookId, BookStoreId, Url) "
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

    def get_bookstores_for_books(self, books: list[Book]) -> dict[int, list[BookInBookStore]]:
        book_dict = {b.id: b for b in books}
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(book_dict.keys()))
                query = ("SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " 
                         "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " 
                         "bs.PriceFormat, bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector, "
                         "bs.IsbnCssSelector, bs.ColorHex, bs.ScraperId " 
                         "FROM BookStoreBook bsb " 
                         "JOIN BookStore bs ON bs.Id = bsb.BookStoreId " 
                         f"WHERE bsb.BookId IN ({ids_format_string})")

                cursor.execute(query, tuple(book_dict.keys()))

                books_in_bookstore = {}
                bookstores = {}
                for row in cursor:
                    bookstore_id = row["BookStoreId"]
                    if bookstore_id not in bookstores:
                        bookstores[bookstore_id] = self._map_bookstore(row)

                    book_id = row["BookId"]
                    if book_id not in books_in_bookstore:
                        books_in_bookstore[book_id] = []
                    books_in_bookstore[book_id].append(BookInBookStore(book_dict[book_id],
                                                                       bookstores[bookstore_id],
                                                                       row["BookUrl"]))

        return books_in_bookstore

    def get_bookstores_with_image_source_for_books(self, books: list[Book]) -> dict[int, list[BookInBookStore]]:
        book_dict = {b.id: b for b in books}
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(book_dict.keys()))
                query = ("SELECT bsb.BookId, bsb.BookStoreId, bsb.Url as BookUrl, " 
                         "bs.Name as BookStoreName, bs.Url as BookStoreUrl, bs.PriceCssSelector, " 
                         "bs.PriceFormat, bs.SearchUrl, bs.SearchResultCssSelector, bs.ImageCssSelector, "
                         "bs.IsbnCssSelector, bs.ColorHex, bs.ScraperId " 
                         "FROM BookStoreBook bsb " 
                         "JOIN BookStore bs ON bs.Id = bsb.BookStoreId " 
                         f"WHERE bsb.BookId IN ({ids_format_string}) AND bs.ImageCssSelector IS NOT NULL;")

                cursor.execute(query, tuple(book_dict.keys()))

                books_in_bookstore = defaultdict(list)
                bookstores = {}
                for row in cursor:
                    bookstore_id = row["BookStoreId"]
                    if bookstore_id not in bookstores:
                        self._add_bookstore_from_row(row, bookstores)

                    book_id = row["BookId"]
                    books_in_bookstore[book_id].append(BookInBookStore(book_dict[book_id],
                                                                       bookstores[bookstore_id],
                                                                       row["BookUrl"]))

        return books_in_bookstore

    @classmethod
    def _add_bookstore_from_row(cls, row: dict, bookstore_dict: dict[int, BookStore]):
        bookstore_id = row["BookStoreId"]
        bookstore_dict[bookstore_id] = cls._map_bookstore(row)

    @staticmethod
    def _map_bookstore(row: dict) -> BookStore:
        return BookStore(
            id=row["BookStoreId"],
            name=row["BookStoreName"],
            url=row["BookStoreUrl"],
            search_url=row["SearchUrl"],
            search_result_css_selector=row["SearchResultCssSelector"],
            price_css_selector=row["PriceCssSelector"],
            image_css_selector=row["ImageCssSelector"],
            isbn_css_selector=row["IsbnCssSelector"],
            price_format=row["PriceFormat"],
            color_hex=row["ColorHex"],
            scraper_id=row["ScraperId"])
