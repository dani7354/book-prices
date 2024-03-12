from dataclasses import dataclass, field
from typing import Optional, ClassVar
from collections import defaultdict
from bookprices.shared.model.book import Book
from bookprices.shared.model.bookstore import BookStore
from bookprices.shared.validation.isbn import check_isbn13


@dataclass(frozen=True)
class AuthorOption:
    text: str
    value: str
    selected: bool


@dataclass(frozen=True)
class SortingOption:
    text: str
    url: str
    selected: bool


@dataclass(frozen=True)
class BookListItemViewModel:
    id: int
    isbn: str
    title: str
    author: str
    url: str
    image_url: str


@dataclass(frozen=True)
class BookPriceForStoreViewModel:
    book_store_id: int
    book_store_name: str
    url: str
    price_history_url: str
    price: float
    created: str
    is_price_available: bool


@dataclass(frozen=True)
class PriceHistoryViewModel:
    book: Book
    book_store: BookStore
    store_url: str
    return_url: str


@dataclass(frozen=True)
class SearchViewModel:
    book_list: list[BookListItemViewModel]
    authors: list[AuthorOption]
    sorting_options: list[SortingOption]
    search_phrase: str
    author: Optional[str]
    current_page: int
    previous_page: Optional[int]
    next_page: Optional[int]
    previous_page_url: Optional[str]
    next_page_url: Optional[str]


@dataclass(frozen=True)
class BookDetailsViewModel:
    book: Book
    book_prices: list[BookPriceForStoreViewModel]
    return_url: str
    author_search_url: str
    page: Optional[int]
    search_phrase: Optional[str]


@dataclass(frozen=True)
class CreateBookViewModel:
    title_field_name: ClassVar[str] = "title"
    author_field_name: ClassVar[str] = "author"
    isbn_field_name: ClassVar[str] = "isbn"
    format_field_name: ClassVar[str] = "format"

    _title_min_length: ClassVar[int] = 2
    _title_max_length: ClassVar[int] = 255
    _author_min_length: ClassVar[int] = 2
    _author_max_length: ClassVar[int] = 255
    _isbn_min_length: ClassVar[int] = 13
    _isbn_max_length: ClassVar[int] = 13
    _format_min_length: ClassVar[int] = 2
    _format_max_length: ClassVar[int] = 255

    isbn: str
    title: str
    author: str
    format: str
    errors: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def is_valid(self) -> bool:
        return not self.validate_input()

    def validate_input(self) -> None:
        if len(self.title) < self._title_min_length:
            self.errors[self.title_field_name].append(
                f"Title must be at least {self._title_min_length} characters long")
        if len(self.title) > self._title_max_length:
            self.errors[self.title_field_name].append(f"Title must be at most {self._title_max_length} characters long")
        if len(self.author) < self._author_min_length:
            self.errors[self.author_field_name].append(
                f"Author must be at least {self._author_min_length} characters long")
        if len(self.author) > self._author_max_length:
            self.errors[self.author_field_name].append(
                f"Author must be at most {self._author_max_length} characters long")
        if len(self.isbn) < self._isbn_min_length:
            self.errors[self.isbn_field_name].append(f"ISBN must be at least {self._isbn_min_length} characters long")
        if len(self.isbn) > self._isbn_max_length:
            self.errors[self.isbn_field_name].append(f"ISBN must be at most {self._isbn_max_length} characters long")
        if not check_isbn13(self.isbn):
            self.errors[self.isbn_field_name].append("ISBN is not valid")
        if len(self.format) < self._format_min_length:
            self.errors[self.format_field_name].append(
                f"Format must be at least {self._format_min_length} characters long")
        if len(self.format) > self._format_max_length:
            self.errors[self.format_field_name].append(
                f"Format must be at most {self._format_max_length} characters long")

    def add_error(self, field_name: str, message: str) -> None:
        self.errors[field_name].append(message)

    @staticmethod
    def empty() -> "CreateBookViewModel":
        return CreateBookViewModel("", "", "", "")

