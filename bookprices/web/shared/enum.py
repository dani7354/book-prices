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


class CacheTtlOption(IntEnum):  # In seconds
    SHORT = 60 * 5
    MEDIUM = 60 * 60
    LONG = 60 * 60 * 24


class Endpoint(Enum):
    PAGE_INDEX = "page.index"
    PAGE_ABOUT = "page.about"
    PAGE_LOGIN = "page.login"
    BOOK = "book.book"
    BOOK_CREATE = "book.create"
    BOOK_EDIT = "book.edit"
    BOOK_PRICE_HISTORY = "book.price_history"
    BOOK_SEARCH = "book.search"
    JOB_INDEX = "job.index"
    JOB_EDIT = "job.edit"
    JOB_CREATE_JOB_RUN = "job.create_job_run"
    JOB_UPDATE_JOB_RUN = "job.update_job_run"


class SessionKey(Enum):
    STATE = "state"
    REDIRECT_URL = "redirect_url"


class BookTemplate(Enum):
    SEARCH = "book/search.html"
    BOOK = "book/book.html"
    CREATE = "book/create.html"
    EDIT = "book/edit.html"
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


class JobTemplate(Enum):
    INDEX = "job/index.html"
    CREATE = "job/create.html"
    EDIT = "job/edit.html"
