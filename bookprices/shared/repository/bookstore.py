from collections import defaultdict
from typing import Tuple, Sequence

from sqlalchemy import select, and_, outerjoin
from sqlalchemy.orm import joinedload

from bookprices.shared.db.tables import BookStore, BookStoreBook, Book
from bookprices.shared.repository.base import RepositoryBase


class BookStoreRepository(RepositoryBase[BookStore]):

    def __init__(self, session) -> None:
        super().__init__(session)

    @property
    def entity_type(self) -> type:
        return BookStore

    def get_bookstores_for_books(self, book_ids: Sequence[int]) -> dict[int, list[BookStoreBook]]:
        entities = (self._session.execute(
            select(BookStoreBook)
            .options(joinedload(BookStoreBook.book))
            .options(joinedload(BookStoreBook.book_store))
            .where(BookStoreBook.book_id.in_(book_ids)))
            .scalars()
            .all())
        self._session.expunge_all()

        bookstores_by_book_id = defaultdict(list)
        for bookstore_book in entities:
            bookstores_by_book_id[bookstore_book.book_id].append(bookstore_book)

        return bookstores_by_book_id

    def get_missing_bookstores_by_isbn(self, offset: int, limit: int) -> dict[Tuple[int, str], list[BookStore]]:
            stmt = (
                select(
                    Book.id.label("BookId"),
                    Book.isbn,
                    BookStore.id.label("BookStoreId"),
                    BookStore
                )
                .select_from(
                    Book, outerjoin(BookStoreBook, and_(BookStoreBook.book_id == Book.id, BookStoreBook.book_store_id == BookStore.id)))
                .where(BookStoreBook.book_id == None, BookStoreBook.book_id == None, BookStore.search_url != None)
                .order_by(Book.id.desc())
                .limit(limit)
                .offset(offset)
            )

            entities = self._session.execute(stmt)
            self._session.expunge_all()

            missing_bookstores_by_book_id_isbn_and_id = defaultdict(list)
            for row in entities:
                book_id = row.BookId
                isbn = row.isbn
                bookstore = row.BookStore
                missing_bookstores_by_book_id_isbn_and_id[(book_id, isbn)].append(bookstore)

            return missing_bookstores_by_book_id_isbn_and_id

    def add_books_to_bookstores(self, bookstores_for_books: Tuple[int, int, str]):
        """ Creating multiple BookStoreBook row tuple argument order: (book_id, bookstore_id, url) """
        book_store_entries = [
            BookStoreBook(book_id=book_id, book_store_id=bookstore_id, url=url)
            for book_id, bookstore_id, url in bookstores_for_books
        ]
        self._session.bulk_save_objects(book_store_entries)

    def add_book_to_bookstore(self, book_id: int, bookstore_id: int, url: str) -> None:
        book_store = BookStoreBook(book_id=book_id, book_store_id=bookstore_id, url=url)
        self._session.add(book_store)

    def update(self, entity: BookStore) -> None:
        if not (existing_entity := self._session.get(BookStore, entity.id)):
            raise ValueError(f"BookStore with id {entity.id} not found.")

        existing_entity.name = entity.name
        existing_entity.url = entity.url
        existing_entity.search_url = entity.search_url
        existing_entity.search_result_css_selector = entity.search_result_css_selector
        existing_entity.image_css_selector = entity.image_css_selector
        existing_entity.isbn_css_selector = entity.isbn_css_selector
        existing_entity.price_css_selector = entity.price_css_selector
        existing_entity.price_format = entity.price_format
        existing_entity.color_hex = entity.color_hex
        existing_entity.scraper_id = entity.scraper_id

        self._session.merge(existing_entity)

    def delete_book_from_bookstore(self, book_id: int, bookstore_id: int) -> None:
        book_store = (self._session.execute(
            select(BookStore)
            .filter_by(book_id=book_id, bookstore_id=bookstore_id))
            .scalars()
            .first())

        if not book_store:
            raise ValueError(f"BookStore entry for book id {book_id} and bookstore id {bookstore_id} doesn't exist.")
        self._session.delete(book_store)