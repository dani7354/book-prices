import re
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import bookprices.shared.webscraping.options as options


class PriceNotFoundException(Exception):
    pass


class PriceFinder:
    FALLBACK_PRICE_FORMAT = r".*"

    @classmethod
    def get_price(cls, url, price_css_path, price_format) -> float:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as ex:
            raise PriceNotFoundException(ex)

        price = cls._parse_price(response.content.decode(), price_css_path, price_format)

        return price

    @classmethod
    def _parse_price(cls, response_content, css_path, price_format) -> float:
        if not price_format:
            price_format = cls.FALLBACK_PRICE_FORMAT

        content_bs = BeautifulSoup(response_content, options.BS_HTML_PARSER)
        price_html = content_bs.select_one(css_path)
        if not price_html:
            raise PriceNotFoundException(f"No match for {css_path} in the response body!")

        price_format_match = re.search(price_format, price_html.get_text())
        if not price_format_match:
            raise PriceNotFoundException(f"No match for the price format {price_format}")

        try:
            price_value = float(price_format_match.group().replace(",", "."))
        except ValueError:
            raise PriceNotFoundException(f"Could not convert the price text to a float: {price_format_match[0]}!")

        return price_value
