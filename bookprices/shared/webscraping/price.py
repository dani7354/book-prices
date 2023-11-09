import re
import requests
import bookprices.shared.webscraping.options as options
from typing import Optional
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup


FALLBACK_PRICE_FORMAT = r".*"


class PriceNotFoundException(Exception):
    pass


class PriceSelectorError(Exception):
    pass


class PriceFormatError(Exception):
    pass


class PriceFinderConnectionError(Exception):
    pass


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
        response = requests.get(url)
        response.raise_for_status()
        price = _parse_price(response.content.decode(), css_selector, price_format)

        return price
    except ConnectionError as ex:
        raise PriceFinderConnectionError(f"Something went wrong while trying to reach {url}: {ex}")
    except HTTPError as ex:
        raise PriceNotFoundException(f"Page not found {url}: {ex}")
