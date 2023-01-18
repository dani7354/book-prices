#!/usr/bin/env python3
import requests
import re
from bs4 import BeautifulSoup

class WebSource:
    def __init__(self, url, price_css_path, price_format):
        self.url = url
        self.price_css_path = price_css_path
        self.price_format = price_format

    def get_price(self, url, price_css_path, price_format):
        response = requests.get(url)
        price = self._parse_price(response.content.decode(), price_css_path, price_format)

        return price

    def _parse_price(self, response_content, css_path, price_format) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html = content_bs.select_one(css_path).get_text()
        price_format_match = re.search(price_format, price_html)
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value



class Saxo:
    BASE_URL = "https://www.saxo.com"
    PRICE_CSS_PATH = "div.membership-price-block label"
    PRICE_FORMAT = r"\d+,\d{2}"

    @classmethod
    def parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_format_match = re.search(cls.PRICE_FORMAT, price_html)
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls.parse_price(response.content.decode())

        return price


class WilliamDam:
    BASE_URL = "https://www.williamdam.dk"
    PRICE_CSS_PATH = "#wd_prices_product > div:nth-child(2) > span:nth-child(1)"
    PRICE_FORMAT = r"\d+"

    @classmethod
    def parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_format_match = re.search(cls.PRICE_FORMAT, price_html)
        price_value = float(price_format_match.group())

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls.parse_price(response.content.decode())

        return price


class PlusBog:
    BASE_URL = "https://www.plusbog.dk"
    PRICE_CSS_PATH = "#inactiveOptionContainer > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)"

    @classmethod
    def parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_value = float(price_html)

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls.parse_price(response.content.decode())

        return price


class Gucca:
    BASE_URL = "https://www.gucca.dk"
    PRICE_CSS_PATH = ".current-price"
    PRICE_FORMAT = r"\d+,\d{2}"

    @classmethod
    def parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_format_match = re.search(cls.PRICE_FORMAT, price_html)
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls.parse_price(response.content.decode())

        return price

class BogOgIde:
    BASE_URL = "https://www.bog-ide.dk"
    PRICE_CSS_PATH = ".css-bdecq7-Grid > div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > div:nth-child(3)"
    PRICE_FORMAT = r"\d+,\d{2}"

    @classmethod
    def parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_format_match = re.search(cls.PRICE_FORMAT, price_html)
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls.parse_price(response.content.decode())

        return price


class CoopShopping:
    BASE_URL = "https://shopping.coop.dk"
    PRICE_CSS_PATH = ".memberprice > span:nth-child(1)"
    PRICE_FORMAT = r"\d+,\d{2}"

    @classmethod
    def _parse_price(cls, response_content) -> float:
        content_bs = BeautifulSoup(response_content, "html.parser")
        price_html =  content_bs.select_one(cls.PRICE_CSS_PATH).get_text()
        price_format_match = re.search(cls.PRICE_FORMAT, price_html)
        price_value = float(price_format_match.group().replace(",", "."))

        return price_value


    @classmethod
    def get_price(cls, url):
        full_url = f"{cls.BASE_URL}{url}"
        response = requests.get(full_url)
        price = cls._parse_price(response.content.decode())

        return price



test_url = "/dk/farskibet_glenn-bech_haeftet_9788702309423"
price = Saxo.get_price(test_url)
print(f"Saxo: {price}")

test_url = "/farskibet__1787442"
price = WilliamDam.get_price(test_url)
print(f"WilliamDam: {price}")

test_url = "/farskibet-glenn-bech-9788702309423"
price = PlusBog.get_price(test_url)
print(f"PlusBog: {price}")

test_url = "/farskibet-bog-p507625"
price = Gucca.get_price(test_url)
print(f"Gucca: {price}")

test_url = "/produkt/2692651/glenn-bech-farskibet-haeftet/2873131"
price = BogOgIde.get_price(test_url)
print(f"Bog og ide: {price}")

test_url = "/vare/farskibet-haeftet-af-glenn-bech/9788702309423"
price = CoopShopping.get_price(test_url)
print(f"Coop shopping: {price}")



