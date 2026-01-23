import logging
import re
import requests
import bookprices.shared.webscraping.options as options
from abc import ABC, abstractmethod
from typing import Optional
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import HttpClient, RequestFailedError, RateLimiter

FALLBACK_PRICE_FORMAT = r".*"


class PriceNotFoundException(Exception):
    pass


class PriceSelectorError(Exception):
    pass


class PriceFormatError(Exception):
    pass


class PriceFinderConnectionError(Exception):
    pass


class PriceScraper(ABC):
    """ Abstract base class for price scrapers."""
    def __init__(self) -> None:
        self._http_client = HttpClient()

    @abstractmethod
    def get_price(self, url: str) -> float:
        raise NotImplementedError


class StaticHtmlPriceScraper(PriceScraper):
    """ Price scraper for static HTML content. """

    def __init__(self, price_css_selector: str, price_format: str | None) -> None:
        super().__init__()
        self._price_css_selector = price_css_selector
        self._price_format = price_format or FALLBACK_PRICE_FORMAT
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_price(self, url: str) -> float:
        with HttpClient() as http_client:
            try:
                response = http_client.get(url)
                if response.text:
                    return self._parse_price(response.text)
                raise PriceNotFoundException
            except RequestFailedError as ex:
                raise PriceNotFoundException from ex

    def _parse_price(self, response_text: str) -> float:
        html_content = HtmlContent(response_text)
        if not (
        price_text := html_content.find_element_text_by_css(self._price_css_selector)):
            raise PriceSelectorError

        if not (price_match := re.search(self._price_format, price_text)):
            raise PriceFormatError

        try:
            return float(price_match.group().replace(",", "."))
        except ValueError as ex:
            self._logger.error(f"Failed to parse value as float: {price_match.group()}")
            raise PriceFormatError from ex


class RateLimitedStaticHtmlPriceScraper(PriceScraper):
    """ StatisHtmlPriceScraper extended with rate limiting between requests. """

    def __init__(
            self,
            price_css_selector: str,
            price_format: str | None,
            max_requests: int,
            period_seconds: int) -> None:
        super().__init__()
        self._rate_limiter = RateLimiter(max_requests, period_seconds)
        self._scraper = StaticHtmlPriceScraper(price_css_selector, price_format)
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_price(self, url: str) -> float:
        self._rate_limiter.wait_if_needed()
        return self._scraper.get_price(url)


def _parse_price(response_content: str, css_path: str, price_format: Optional[str]) -> float:
    if not price_format:
        price_format = FALLBACK_PRICE_FORMAT

    content_bs = BeautifulSoup(response_content, options.BS_HTML_PARSER)
    if not (price_html := content_bs.select_one(css_path)):
        raise PriceSelectorError(f"No match for {css_path} in the response body!")

    if not (price_format_match := re.search(price_format, price_html.get_text())):
        raise PriceSelectorError(f"No match for the price format {price_format}")

    try:
        price_value = float(price_format_match.group().replace(",", "."))
    except ValueError:
        raise PriceFormatError(f"Could not convert the price text to a float: {price_format_match[0]}!")

    return price_value


def get_price(url: str, css_selector: str, price_format: Optional[str]) -> float:
    try:
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        if response.status_code in (301, 302):
            raise PriceNotFoundException(
                f"Price not found {url}: Redirected to {response.headers['Location']} ({response.status_code})")
        price = _parse_price(response.content.decode(), css_selector, price_format)

        return price
    except ConnectionError as ex:
        raise PriceFinderConnectionError(f"Something went wrong while trying to reach {url}: {ex}")
    except HTTPError as ex:
        raise PriceNotFoundException(f"Page not found {url}: {ex}")
