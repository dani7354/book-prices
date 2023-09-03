from datetime import datetime
from typing import Optional
from bookprices.shared.db.base import BaseDb
from bookprices.shared.model.book import Book


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

    def search_books(self, search_phrase: str, author: Optional[str], page: int, page_size: int) -> list[Book]:
        with self.get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                phrase_with_wildcards = f"{search_phrase}%"
                parameters = [phrase_with_wildcards,
                              phrase_with_wildcards,
                              search_phrase]
                query = ("SELECT Id, Isbn, Title, Author, Format, ImageUrl, Created "
                         "FROM Book "
                         "WHERE (Title LIKE %s OR Author LIKE %s OR Isbn = %s) ")
                if author:
                    query += "AND Author = %s "
                    parameters.append(author)
                query += ("ORDER BY Title ASC "
                          "LIMIT %s "
                          "OFFSET %s;")
                parameters.append(page_size)
                parameters.append((page - 1) * page_size)
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
