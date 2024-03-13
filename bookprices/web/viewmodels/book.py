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

    title_min_length: ClassVar[int] = 1
    title_max_length: ClassVar[int] = 255
    author_min_length: ClassVar[int] = 1
    author_max_length: ClassVar[int] = 255
    isbn_min_length: ClassVar[int] = 13
    isbn_max_length: ClassVar[int] = 13
    format_min_length: ClassVar[int] = 3
    format_max_length: ClassVar[int] = 255

    isbn: str
    title: str
    author: str
    format: str
    errors: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def is_valid(self) -> bool:
        return not self.validate_input()

    def validate_input(self) -> None:
        def min_length_not_met(field_name: str, min_length: int) -> str:
            return f"{field_name} skal være mindst {min_length} tegn"

        def max_length_exceeded(field_name: str, max_length: int) -> str:
            return f"{field_name} må maks. være {max_length} tegn"

        if len(self.title.strip()) < self.title_min_length:
            self.errors[self.title_field_name].append(min_length_not_met("Titlen", self.title_min_length))
        if len(self.title.strip()) > self.title_max_length:
            self.errors[self.title_field_name].append(max_length_exceeded("Titlen", self.title_max_length))
        if len(self.author.strip()) < self.author_min_length:
            self.errors[self.author_field_name].append(
                min_length_not_met("Forfatter", self.author_min_length))
        if len(self.author.strip()) > self.author_max_length:
            self.errors[self.author_field_name].append(
                max_length_exceeded("Forfatter", self.author_max_length))
        if len(self.isbn.strip()) < self.isbn_min_length:
            self.errors[self.isbn_field_name].append(min_length_not_met("ISBN", self.isbn_min_length))
        if len(self.isbn.strip()) > self.isbn_max_length:
            self.errors[self.isbn_field_name].append(max_length_exceeded("ISBN", self.isbn_max_length))
        if not check_isbn13(self.isbn.strip()):
            self.errors[self.isbn_field_name].append("ISBN er ikke gyldig")
        if len(self.format.strip()) < self.format_min_length:
            self.errors[self.format_field_name].append(min_length_not_met("Format", self.format_min_length))
        if len(self.format.strip()) > self.format_max_length:
            self.errors[self.format_field_name].append(max_length_exceeded("Format", self.format_max_length))

    def add_error(self, field_name: str, message: str) -> None:
        self.errors[field_name].append(message)

    @staticmethod
    def empty() -> "CreateBookViewModel":
        return CreateBookViewModel("", "", "", "")

