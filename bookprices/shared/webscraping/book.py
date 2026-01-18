import logging
import threading
from abc import ABC, abstractmethod
from collections import Counter

import requests
from requests import RequestException, Response
from urllib.parse import urljoin, urlparse
from typing import ClassVar
from bs4 import BeautifulSoup
from dataclasses import dataclass, replace
from bookprices.shared.webscraping import options
from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import HttpClient, HttpResponse

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


class BookFinder:
    """ Class for searching for books in a bookstore """
    request_timeout_seconds: ClassVar[int] = 5
    match_url_request_limit: ClassVar[int] = 5
    href_attribute: ClassVar[str] = "href"
    encoding: ClassVar[str] = "utf-8"

    def __init__(
            self,
            bookstore_id: int,
            bookstore_name: str,
            bookstore_url: str,
            search_url: str,
            bookstore_isbn_css_selector: str | None,
            search_result_css_selector: str | None,
            redirects_on_match: bool = False) -> None:
        self.bookstore_id = bookstore_id
        self.bookstore_name = bookstore_name
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._bookstore_isbn_css_selector = bookstore_isbn_css_selector
        self._search_result_css_selector = search_result_css_selector
        self._redirects_on_match = redirects_on_match
        self._lock =  threading.Lock()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        self._url_request_count = Counter()

    def find_url_for_book(self, book_id: int, isbn: str) -> SearchResult | None:
        try:
            search_url = self._search_url.format(isbn)
            self._logger.debug(f"Searching for book {book_id} with ISBN {isbn} at {search_url}")
            if not (match_url := self._get_match_url(search_url)):
                self._logger.info(f"No match found for book {book_id} with ISBN {isbn} at {search_url}")
                return None

            if not self._is_match_url_valid(match_url, isbn):
                self._logger.debug(f"URL {match_url} is not valid for book {book_id} with ISBN {isbn}.")
                return None

            self._logger.info(f"Found match for book {book_id} with ISBN {isbn} at {match_url}")
            return SearchResult(bookstore_id=self.bookstore_id, url=match_url)
        except (RequestException, UnicodeDecodeError) as ex:
            self._logger.error(f"Failed to format search URL for book {book_id} with ISBN {isbn}: {ex}")
            return None

    def _get_match_url(self, search_url: str) -> str | None:
        response = requests.get(search_url, headers=self._request_headers, timeout=self.request_timeout_seconds)
        response.raise_for_status()

        if self._redirects_on_match:
            if self._was_redirected_to_detail_page(response):
                return response.url
        else:
            return None

        if not (content_bs := BeautifulSoup(response.content.decode(self.encoding), options.BS_HTML_PARSER)):
            raise BookNotFoundError(f"Failed to parse response content from {search_url}")
        if (not self._search_result_css_selector
                or not (match_url_tag := content_bs.select_one(self._search_result_css_selector))):
            raise BookNotFoundError(f"No match found for CSS selector {self._search_result_css_selector} at {search_url}")

        return match_url_tag.get(self.href_attribute)

    def _is_match_url_valid(self, match_url: str, isbn: str) -> bool:
        if isbn in match_url:
            return True

        full_match_url = urljoin(self._bookstore_url, urlparse(match_url).path)
        if self._url_request_count[full_match_url] > self.match_url_request_limit:
            self._logger.info(
                f"Requests to {full_match_url} has exceeded the limit of {self.match_url_request_limit}. Skipping check.")
            return False

        self._logger.debug(f"Checking if match URL {full_match_url} is valid for ISBN {isbn}")
        response = requests.get(full_match_url, timeout=self.request_timeout_seconds)
        response.raise_for_status()
        with self._lock:
            self._url_request_count[full_match_url] += 1

        response_body = response.content.decode(self.encoding)
        response_bs = BeautifulSoup(response_body, options.BS_HTML_PARSER)
        if (not self._bookstore_isbn_css_selector
                or not (isbn_element := response_bs.select_one(self._bookstore_isbn_css_selector))):
            self._logger.error(
                f"Failed to parse response body from {match_url}. "
                f"CSS selector {self._bookstore_isbn_css_selector} not found.")
            return False

        return isbn in str(isbn_element) or isbn in response_body


    @staticmethod
    def _was_redirected_to_detail_page(response: Response) -> bool:
        return (len(response.history) > 0
                and response.history[0].status_code in {REDIRECTED_PERMANENT, REDIRECTED_TEMPORARY})