import re
import requests
import bookprices.shared.webscraping.options as options
from typing import Optional
from requests.exceptions import HTTPError
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup


class PriceNotFoundException(Exception):
    pass


class PriceFinder:
    FALLBACK_PRICE_FORMAT = r".*"

    @classmethod
    def get_price(cls, url: str, css_selector: str, price_format: Optional[str]):
        pass


class PriceFinderStatic(PriceFinder):
    @classmethod
    def get_price(cls, url: str, css_selector: str, price_format: Optional[str]) -> float:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as ex:
            raise PriceNotFoundException(f"Something went wrong while trying to reach {url}: {ex}")

        price = cls._parse_price(response.content.decode(), css_selector, price_format)

        return price

    @classmethod
    def _parse_price(cls, response_content: str, css_path: str, price_format: Optional[str]) -> float:
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


class PriceFinderDynamic(PriceFinder):
    DYNAMIC_ELEMENT_WAIT_TIMEOUT = 10

    @classmethod
    def get_price(cls, url: str, css_selector: str, price_format: Optional[str]) -> float:
        driver_options = Options()
        driver_options.add_argument("--headless")
        try:
            with Firefox(options=driver_options) as driver:
                driver.get(url)

                price_element = WebDriverWait(driver, timeout=cls.DYNAMIC_ELEMENT_WAIT_TIMEOUT).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
        except WebDriverException as ex:
            raise PriceNotFoundException(f"Something went wrong while getting price from {url}: {ex}")

        return cls._parse_price(price_element.text, price_format)

    @classmethod
    def _parse_price(cls, price_str: str, price_format: str) -> float:
        if not price_format:
            price_format = cls.FALLBACK_PRICE_FORMAT

        price = re.search(price_format, price_str)
        if not price:
            raise PriceNotFoundException(f"No match for the price format {price_format}")

        return float(price.group().replace(",", "."))


class PriceFinderFactory:
    @classmethod
    def get_price_finder(cls, has_dynamically_loaded_content: bool) -> PriceFinder:
        return PriceFinderDynamic() if has_dynamically_loaded_content else PriceFinderStatic()
