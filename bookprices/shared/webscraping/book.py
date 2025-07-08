import logging
import threading
from collections import Counter

import requests
from requests import RequestException, Response
from urllib.parse import urljoin, urlparse
from typing import ClassVar
from bs4 import BeautifulSoup
from dataclasses import dataclass
from bookprices.shared.webscraping import options


REDIRECTED_PERMANENT = 301
REDIRECTED_TEMPORARY = 302


class BookNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class BookSearchResult:
    book_id: int
    bookstore_id: int
    url: str


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

    def find_url_for_book(self, book_id: int, isbn: str) -> BookSearchResult | None:
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
            return BookSearchResult(book_id=book_id, bookstore_id=self.bookstore_id, url=match_url)
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
        if not (match_url_tag := content_bs.select_one(self._search_result_css_selector)):
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
        if not (isbn_element := response_bs.select_one(self._bookstore_isbn_css_selector)):
            self._logger.error(
                f"Failed to parse response body from {match_url}. "
                f"CSS selector {self._bookstore_isbn_css_selector} not found.")
            return False

        return isbn in str(isbn_element) or isbn in response_body


    @staticmethod
    def _was_redirected_to_detail_page(response: Response) -> bool:
        return (len(response.history) > 0
                and response.history[0].status_code in {REDIRECTED_PERMANENT, REDIRECTED_TEMPORARY})