import logging
import re
from abc import ABC, abstractmethod

from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.currency import CurrencyConverter
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


class RateLimitedStaticHtmlPriceScraper(StaticHtmlPriceScraper):
    """ StaticHtmlPriceScraper extended with rate limiting between requests. """

    def __init__(
            self,
            price_css_selector: str,
            price_format: str | None,
            max_requests: int,
            period_seconds: int) -> None:
        super().__init__(price_css_selector, price_format)
        self._rate_limiter = RateLimiter(max_requests, period_seconds)
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_price(self, url: str) -> float:
        self._rate_limiter.wait_if_needed()
        return super().get_price(url)


class GuccaStaticHtmlPriceScraper(RateLimitedStaticHtmlPriceScraper):
    """ Price scraper for Gucca.dk bookstore. """

    def __init__(
            self, price_css_selector: str, price_format: str | None, max_requests: int, period_seconds: int) -> None:
        super().__init__(price_css_selector, price_format, max_requests, period_seconds)
        self._currency_converter = CurrencyConverter()

    def _parse_price(self, response_text: str) -> float:
        html_content = HtmlContent(response_text)
        if not (
                price_text := html_content.find_element_text_by_css(self._price_css_selector)):
            raise PriceSelectorError

        if not (price_match := re.search(self._price_format, price_text)):
            raise PriceFormatError

        try:
            price_value = float(price_match.group().replace(",", "."))
            if self.price_in_sek(price_text):
                price_value = self._currency_converter.convert_to_dkk(price_value, "SEK")

            return price_value
        except ValueError as ex:
            self._logger.error(f"Failed to parse value as float: {price_match.group()}")
            raise PriceFormatError from ex

    @staticmethod
    def price_in_sek(price_text: str) -> bool:
        return "SEK" in price_text