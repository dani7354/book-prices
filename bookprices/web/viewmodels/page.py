from dataclasses import dataclass
from bookprices.shared.model.bookstore import BookStore
from bookprices.web.viewmodels.book import BookListItemViewModel


@dataclass(frozen=True)
class IndexViewModel:
    newest_books: list[BookListItemViewModel]
    latest_prices_books: list[BookListItemViewModel]
    newest_books_url: str


@dataclass(frozen=True)
class AboutViewModel:
    bookstores: list[BookStore]


@dataclass(frozen=True)
class LoginViewModel:
    google_client_id: str
    google_redirect_uri: str
