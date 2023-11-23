from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.book import Book


class BookSearchSortOption(Enum):
    Author = "Author"
    Title = "Title"
    Created = "Created"

    @staticmethod
    def from_str(value: Optional[str]) -> Optional["BookSearchSortOption"]:
        if not value:
            return None
        try:
            return BookSearchSortOption(value)
        except ValueError:
            return None


@dataclass(frozen=True)
class SearchQuery:
    search_phrase: str
    author: Optional[str]
    page: int
    page_size: int
    sort_option: BookSearchSortOption
    sort_in_descending_order: bool

    def clone(self,
              search_phrase: Optional[str] = None,
              author: Optional[str] = None,
              page: Optional[int] = None,
              page_size: Optional[int] = None,
              sort_option: Optional[BookSearchSortOption] = None,
              sort_in_descending_order: Optional[bool] = None):

        return SearchQuery(
            search_phrase=search_phrase if search_phrase else self.search_phrase,
            author=author if author else self.author,
            page=page if page else self.page,
            page_size=page_size if page_size else self.page_size,
            sort_option=sort_option if sort_option else self.sort_option,
            sort_in_descending_order=sort_in_descending_order if sort_in_descending_order else self.sort_in_descending_order)


class BookDb(BaseDb):
    def create_book(self, book: Book) -> int:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = "INSERT INTO Book(Isbn, Title, Author, Format, Created) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(query, (book.isbn, book.title, book.author, book.format, datetime.now()))
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
                         "SET Title = %s, Author = %s, Format = %s, ImageUrl = %s "
                         "WHERE Id = %s;")
                cursor.execute(query, (book.title, book.author, book.format, book.image_url, book.id))
                con.commit()

    def get_books(self) -> list[Book]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         "ORDER BY Title ASC;")
                cursor.execute(query)
                books = []
                for row in cursor:
                    book = Book(row["Id"],
                                row["Isbn"],
                                row["Title"],
                                row["Author"],
                                row["Format"],
                                row["ImageUrl"],
                                row["Created"])
                    books.append(book)

                return books

    def get_books_by_ids(self, ids: set[int]) -> list[Book]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                ids_format_string = ",".join(["%s"] * len(ids))
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         f"WHERE Id IN ({ids_format_string}) "
                         "ORDER BY Title ASC;")
                cursor.execute(query, tuple(ids))
                books = []
                for row in cursor:
                    book = Book(row["Id"],
                                row["Isbn"],
                                row["Title"],
                                row["Author"],
                                row["Format"],
                                row["ImageUrl"],
                                row["Created"])
                    books.append(book)

                return books

    def get_next_book_ids(self, offset: int, limit: int) -> set[int]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id "
                         "FROM Book "
                         "ORDER BY Id "
                         "OFFSET %s LIMIT %s;")

                cursor.execute(query, (offset, limit))
                book_ids = set()
                for row in cursor:
                    book_ids.add(row["BookId"])

                return book_ids

    def search_books(self, search_query: SearchQuery) -> list[Book]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                phrase_with_wildcards = f"{search_query.search_phrase}%"
                parameters = [phrase_with_wildcards,
                              phrase_with_wildcards,
                              search_query.search_phrase]
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         "WHERE (Title LIKE %s OR Author LIKE %s OR Isbn = %s) ")
                if search_query.author:
                    query += "AND Author = %s "
                    parameters.append(search_query.author)

                query += f"ORDER BY {search_query.sort_option.name} "
                query += "DESC " if search_query.sort_in_descending_order else "ASC "
                query += "LIMIT %s OFFSET %s;"

                parameters.append(search_query.page_size)
                parameters.append((search_query.page - 1) * search_query.page_size)
                cursor.execute(query, parameters)
                books = []
                for row in cursor:
                    book = Book(row["Id"],
                                row["Isbn"],
                                row["Title"],
                                row["Author"],
                                row["Format"],
                                row["ImageUrl"],
                                row["Created"])
                    books.append(book)

                return books

    def get_book(self, book_id: int) -> Book:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         "WHERE Id = %s;")
                cursor.execute(query, (book_id,))
                books = []
                for row in cursor:
                    book = Book(row["Id"],
                                row["Isbn"],
                                row["Title"],
                                row["Author"],
                                row["Format"],
                                row["ImageUrl"],
                                row["Created"])
                    books.append(book)

                return books[0] if len(books) > 0 else None

    def get_book_count(self) -> int:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = "SELECT COUNT(*) as BookCount FROM Book;"
                cursor.execute(query)
                for row in cursor:
                    return row["BookCount"]

    def get_book_by_isbn(self, book_id: str) -> Book:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         "WHERE Isbn = %s;")
                cursor.execute(query, (book_id,))
                books = []
                for row in cursor:
                    book = Book(row["Id"],
                                row["Isbn"],
                                row["Title"],
                                row["Author"],
                                row["Format"],
                                row["ImageUrl"],
                                row["Created"])
                    books.append(book)

                return books[0] if len(books) > 0 else None

    def get_authors(self) -> list[str]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT DISTINCT Author "
                         "FROM Book "
                         "ORDER BY Author ASC;")
                cursor.execute(query)
                authors = []
                for row in cursor:
                    authors.append(row["Author"])

                return authors
