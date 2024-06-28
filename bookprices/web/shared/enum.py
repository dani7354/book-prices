from enum import StrEnum, IntEnum, Enum


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"


class HttpStatusCode(IntEnum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class CacheTtl(IntEnum):  # TODO: Add more and change
    SHORT = 60
    MEDIUM = 300
    LONG = 900


class Endpoint(Enum):
    PAGE_INDEX = "page.index"
    ABOUT = "page.about"
    LOGIN = "page.login"
    BOOK = "book.book"
    CREATE = "book.create"
    PRICE_HISTORY = "book.price_history"
    BOOK_SEARCH = "book.search"


class SessionKey(Enum):
    STATE = "state"
    REDIRECT_URL = "redirect_url"


class BookTemplate(Enum):
    SEARCH = "book/search.html"
    BOOK = "book/book.html"
    CREATE = "book/create.html"
    PRICE_HISTORY = "book/price_history.html"


class PageTemplate(Enum):
    INDEX = "index.html"
    ABOUT = "about.html"
    LOGIN = "login.html"
    ERROR_404 = "404.html"
    ERROR_500 = "500.html"


class StatusTemplate(Enum):
    INDEX = "status/index.html"


class UserTemplate(Enum):
    EDIT_USER = "user/edit.html"
