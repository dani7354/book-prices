import re
import requests
from requests import RequestException
from typing import Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
from bookprices.shared.webscraping import options


class BookNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class IsbnSearch:
    search_url: str
    match_css_selector: str
    isbn: str
    isbn_css_selector: str

    def format_url(self) -> str:
        return self.search_url.format(self.isbn)


class BookFinder:
    html_href = "href"
    isbn_patterns = [r"\d{13}"]

    @classmethod
    def search_book_isbn(cls, search_request:  IsbnSearch) -> str:
        try:
            url = search_request.format_url()
            match_url = cls._get_match_url(url, search_request.match_css_selector)
            if not cls._is_match_url_valid(match_url, search_request.isbn_css_selector, search_request.isbn):
                raise BookNotFoundError(f"Invalid url found: {match_url} for ISBN {search_request.isbn}")

            return match_url
        except RequestException as ex:
            raise BookNotFoundError(f"Something went wrong while sending request to {search_request.format_url()}: {ex}")

    @classmethod
    def _get_match_url(cls, url: str, match_url_css: Optional[str]) -> str:
        response = requests.get(url)
        response.raise_for_status()

        if not match_url_css:
            if cls._was_redirected_to_detail_page(response):
                return response.url
            raise BookNotFoundError(f"No match found at {url}")

        content_bs = BeautifulSoup(response.content.decode("utf-8"), options.BS_HTML_PARSER)
        match_url_tag = content_bs.select_one(match_url_css)
        if match_url_tag is None:
            raise BookNotFoundError("Failed to locate match url in response!")

        return match_url_tag[cls.html_href]

    @classmethod
    def _find_isbn(cls, isbn: str) -> str:
        for pattern in cls.isbn_patterns:
            match = re.search(pattern, isbn)
            if match:
                return match.group()

        return ""

    @classmethod
    def _is_match_url_valid(cls, match_url: str, isbn_css: str, book_isbn: str) -> bool:
        response = requests.get(match_url)
        response.raise_for_status()

        response_bs = BeautifulSoup(response.content.decode("utf-8"), options.BS_HTML_PARSER)
        isbn_element = response_bs.select_one(isbn_css)
        isbn = cls._find_isbn(isbn_element.get_text().strip())

        return isbn == book_isbn

    @staticmethod
    def _was_redirected_to_detail_page(response: requests.Response) -> bool:
        return len(response.history) > 0 and response.history[0].status_code in (301, 302)
