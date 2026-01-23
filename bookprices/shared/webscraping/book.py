import logging
from abc import ABC, abstractmethod
from collections import Counter

from urllib.parse import urljoin, urlparse
from typing import ClassVar
from dataclasses import dataclass, replace
from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import HttpClient, HttpResponse, RateLimiter

REDIRECTED_PERMANENT = 301
REDIRECTED_TEMPORARY = 302


class BookNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class SearchResult:
    bookstore_id: int
    url: str | None
    success: bool = False


class BookScraper(ABC):
    """ Abstract base class for book scraper used for searching for books in a bookstore. """

    def __init__(self) -> None:
        """ Should not be instantiated directly. """
        pass

    @abstractmethod
    def find_book(self, isbn: str) -> SearchResult:
        raise NotImplementedError


class RedirectsToDetailPageBookScraper(BookScraper):
    """ Book scraper for bookstores that redirect to the book detail page on search. """
    _timeout_seconds: ClassVar[int] = 5

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            isbn_css_selector: str) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._isbn_css_selector = isbn_css_selector
        self._logger = logging.getLogger(self.__class__.__name__)

    def find_book(self, isbn: str) -> SearchResult:
        search_url = self._search_url.format(isbn)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(search_url)
            if response.redirected and self._is_match_url_valid(response.url, isbn):
                return SearchResult(bookstore_id=self._bookstore_id, url=response.url, success=True)

        return SearchResult(bookstore_id=self._bookstore_id, url=None, success=False)

    def _is_match_url_valid(
            self,
            match_url: str,
            isbn: str) -> bool:
        full_match_url = urljoin(self._bookstore_url, urlparse(match_url).path)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(full_match_url)

        if isbn in response.url:
            return True

        response_bs = HtmlContent(response.text)
        if not (isbn_element := response_bs.find_element_text_by_css(self._isbn_css_selector)):
            self._logger.error(
                f"No matches for ISBN CSS selector in the response body ({response.url, self._isbn_css_selector})")
            return False

        if isbn in str(isbn_element):
            return True

        return False


class RateLimitedRedirectsToDetailPageBookScraper(RedirectsToDetailPageBookScraper):
    """ Book scraper for bookstores that redirect to the book detail page on search, with rate limiting. """

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            isbn_css_selector: str,
            max_requests: int,
            period_seconds: int) -> None:
        super().__init__(bookstore_id, bookstore_url, search_url, isbn_css_selector)
        self._rate_limiter = RateLimiter(max_requests, period_seconds)

    def find_book(self, isbn: str) -> SearchResult:
        self._rate_limiter.wait_if_needed()
        return super().find_book(isbn)


class MatchesInResultListBookScraper(BookScraper):
    """ Book scraper for bookstores that list search results in a result list. """
    _timeout_seconds: ClassVar[int] = 5
    _href_tag : ClassVar[str] = "href"

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            search_result_css_selector: str,
            isbn_css_selector: str) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._search_result_css_selector = search_result_css_selector
        self._isbn_css_selector = isbn_css_selector
        self._logger = logging.getLogger(self.__class__.__name__)

        self._url_request_count = Counter()

    def find_book(self, isbn: str) -> SearchResult:
        search_url = self._search_url.format(isbn)
        search_result = SearchResult(bookstore_id=self._bookstore_id, success=False, url=None)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(search_url)
            if response.redirected:
                self._logger.warning(
                    f"This scraper {self.__class__.__name__} cannot handle redirects.")
                return search_result

            if not (match_url := self._get_match_url(response)):
                return search_result

            if self._is_match_url_valid(isbn, match_url):
                return replace(search_result, url=match_url, success=True)

        return search_result

    def _get_match_url(self, response: HttpResponse) -> str | None:
        content_bs = HtmlContent(response.text)
        if not (match_url := content_bs.find_element_and_get_attribute_value(
                self._search_result_css_selector, self._href_tag)):
            self._logger.error(
                f"Couldn't find match url in the search results ({response.url, self._search_result_css_selector}).")
            return None

        return match_url

    def  _is_match_url_valid(self, isbn: str, match_url: str) -> bool:
        with HttpClient() as http_client:
            response = http_client.get(match_url)
            if response.redirected:
                self._logger.warning(f"Match URL {match_url} redirected to {response.url}.")

        content_bs = HtmlContent(response.text)
        if not (isbn_element := content_bs.find_element_text_by_css(self._isbn_css_selector)):
            self._logger.error(
                f"No matches for ISBN CSS selector in the response body ({response.url, self._isbn_css_selector})")
            return False

        return isbn in str(isbn_element)
