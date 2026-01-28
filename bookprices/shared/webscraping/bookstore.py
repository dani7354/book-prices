import dataclasses
from abc import ABC, abstractmethod
from logging import getLogger
from typing import ClassVar

from bookprices.shared.webscraping.book import RedirectsToDetailPageBookScraper, MatchesInResultListBookScraper, \
    RateLimitedRedirectsToDetailPageBookScraper, RateLimitedMatchesInResultListBookScraper
from bookprices.shared.webscraping.price import PriceScraper, StaticHtmlPriceScraper, RateLimitedStaticHtmlPriceScraper

FALLBACK_PRICE_FORMAT = r".*"


class BookNotFoundError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class BookSearchResult:
    book_id: int
    bookstore_id: int
    url: str


@dataclasses.dataclass(frozen=True)
class BookStoreConfiguration:
    bookstore_id: int
    bookstore_name: str
    bookstore_url: str
    bookstore_search_url: str
    bookstore_price_css_selector: str
    bookstore_price_format: str | None
    bookstore_isbn_css_selector: str | None
    search_result_css_selector: str | None


class BookStoreScraper(ABC):
    """ Base class for BookStore webscraper. """
    name: ClassVar[str]

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        self._configuration = configuration

    @abstractmethod
    def find_book(self, book_id: int, isbn: str) -> BookSearchResult | None:
        raise NotImplementedError

    @abstractmethod
    def get_price(self, url: str) -> float:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        raise NotImplementedError


class StaticBookStoreScraper(BookStoreScraper):
    """
    Scraper for static BookStore websites.
    This scraper assumes that the bookstore website does not load dynamic content via JavaScript and
    that the request is redirected to the book detail page when searching for a book by ISBN
    """

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    _price_format_fallback: ClassVar[str] = FALLBACK_PRICE_FORMAT

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._logger = getLogger(self.__class__.__name__)
        self._price_scraper: PriceScraper = StaticHtmlPriceScraper(
            configuration.bookstore_price_css_selector,
            configuration.bookstore_price_format)

        self._book_scraper = RedirectsToDetailPageBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.bookstore_isbn_css_selector)

    def find_book(self, book_id: int, isbn: str) -> BookSearchResult | None:
        search_result = self._book_scraper.find_book(isbn=isbn)
        return BookSearchResult(
                book_id=book_id,
                bookstore_id=self._configuration.bookstore_id,
                url=search_result.url) if search_result.success else None

    def get_price(self, url: str) -> float:
        return self._price_scraper.get_price(url)


class WilliamDamScraper(StaticBookStoreScraper):
    """ Scraper for WilliamDam.dk bookstore. """
    _max_requests_per_period: ClassVar[int] = 1
    _period_seconds: ClassVar[int] = 2

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._book_scraper = RateLimitedRedirectsToDetailPageBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.bookstore_isbn_css_selector,
            self._max_requests_per_period,
            self._period_seconds)

        self._price_scraper = RateLimitedStaticHtmlPriceScraper(
            configuration.bookstore_price_css_selector,
            configuration.bookstore_price_format,
            self._max_requests_per_period,
            self._period_seconds)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


class SaxoScraper(StaticBookStoreScraper):
    """ Scraper for Saxo.com bookstore. """

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


class BogOgIdeScraper(StaticBookStoreScraper):
    """ Scraper for Bog & Idé bookstore. """

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._book_scraper = MatchesInResultListBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.search_result_css_selector,
            configuration.bookstore_isbn_css_selector)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


class PlusbogScraper(StaticBookStoreScraper):
    """ Scraper for Plusbog.dk bookstore. TODO: needs work! (POST search) """
    _max_requests_per_period: ClassVar[int] = 1
    _period_seconds: ClassVar[int] = 1

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._book_scraper = RateLimitedMatchesInResultListBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.search_result_css_selector,
            configuration.bookstore_isbn_css_selector,
            self._max_requests_per_period,
            self._period_seconds)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


class ThiemersScraper(StaticBookStoreScraper):
    """ Scraper for Thiemers Magasin bookstore. """
    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._book_scraper = RateLimitedMatchesInResultListBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.search_result_css_selector,
            configuration.bookstore_isbn_css_selector,
            max_requests=2,
            period_seconds=1)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


class GuccaScraper(StaticBookStoreScraper):
    """ Scraper for Thiemers Magasin bookstore. """
    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._book_scraper = RateLimitedMatchesInResultListBookScraper(
            configuration.bookstore_id,
            configuration.bookstore_url,
            configuration.bookstore_search_url,
            configuration.search_result_css_selector,
            configuration.bookstore_isbn_css_selector,
            max_requests=2,
            period_seconds=1)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__