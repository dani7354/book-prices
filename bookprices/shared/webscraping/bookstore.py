import dataclasses
from abc import ABC, abstractmethod
from logging import getLogger
from urllib.parse import urlparse, urljoin

from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import RequestFailedError, HttpClient


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
    bookstore_isbn_css_selector: str | None
    search_result_css_selector: str | None


class BookStoreScraper(ABC):
    """ Base class for BookStore webscraper. """

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        self._configuration = configuration

    @abstractmethod
    @property
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def find_book(self, book_id: int, isbn: str) -> BookSearchResult | None:
        raise NotImplementedError

    @abstractmethod
    def get_price(self, url: str) -> float:
        raise NotImplementedError


class StaticBookStoreScraper(BookStoreScraper):
    """ Scraper for static BookStore websites. """

    def __init__(self, configuration: BookStoreConfiguration) -> None:
        super().__init__(configuration)
        self._logger = getLogger(self.__class__.__name__)

    def find_book(self, book_id: int, isbn: str) -> BookSearchResult | None:
        try:
            with HttpClient() as http_client:
                search_url = self._configuration.bookstore_search_url.format(isbn)
                self._logger.debug(f"Searching for book {book_id} with ISBN {isbn} at {search_url}...")
                if not (match_url := self._get_match_url(http_client, search_url)):
                    self._logger.debug(f"No match found for book {book_id} with ISBN {isbn} at {search_url}")
                    return None

                if not self._match_url_valid(http_client, match_url, isbn):
                    self._logger.debug(f"URL {match_url} is not valid for book {book_id} with ISBN {isbn}.")
                    return None

                self._logger.info(f"Found match for book {book_id} with ISBN {isbn} at {match_url}")
                return BookSearchResult(book_id=book_id, bookstore_id=self.bookstore_id, url=match_url)
        except RequestFailedError as ex:
            self._logger.error(f"Failed to format search URL for book {book_id} with ISBN {isbn}: {ex}")
            return None

    @staticmethod
    def _get_match_url(client: HttpClient, search_url: str) -> str | None:
        response = client.get(search_url)
        return response.url if response.redirected else None

    def _match_url_valid(self, client: HttpClient, isbn: str, match_url: str) -> bool:
        if isbn in match_url:
            return True

        full_match_url = urljoin(self._configuration.bookstore_url, urlparse(match_url).path)
        self._logger.debug(f"Checking if match URL {full_match_url} is valid for ISBN {isbn}...")
        response = client.get(full_match_url)

        html_content = HtmlContent(response.text)
        if not (isbn_element := html_content.find_element_text_by_css(self._configuration.bookstore_isbn_css_selector)):
            return False

        return isbn in isbn_element or html_content.contains_text(isbn)

    def get_price(self, url: str) -> float:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__
