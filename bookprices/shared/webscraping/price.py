import re
import requests
from bs4 import BeautifulSoup

import bookprices.shared.webscraping.options as options


class PriceFinder:
    FALLBACK_PRICE_FORMAT = r".*"

    @classmethod
    def get_price(cls, url, price_css_path, price_format) -> float:
        response = requests.get(url)
        price = cls._parse_price(response.content.decode(), price_css_path, price_format)

        return price

    @classmethod
    def _parse_price(cls, response_content, css_path, price_format) -> float:
        if price_format is None:
            price_format = cls.FALLBACK_PRICE_FORMAT

        content_bs = BeautifulSoup(response_content, options.BS_HTML_PARSER)
        price_html = content_bs.select_one(css_path).get_text()
        price_format_match = re.search(price_format, price_html)
        if price_format_match is None:
            raise Exception("Price not found!")
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value
