import os
import pytest
import requests
from bookprices.shared.webscraping.price import PriceFinder, PriceNotFoundException


def mock_get(*args, **kwargs) -> requests.Response:
    fake_response = requests.Response()
    fake_response.status_code = 200
    full_path = os.path.join(os.path.dirname(__file__), "html", "price_format.html")
    with open(full_path, "rb") as html_file:
        fake_response._content = html_file.read()

    return fake_response


@pytest.mark.parametrize("css_selector,value_format",
                         [(".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+\.\d+")])
def test_get_price_value_without_currency(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", mock_get)

    price_finder = PriceFinder()
    price = price_finder.get_price("http://fake.com",
                                   css_selector,
                                   value_format)

    assert price == 229.0


@pytest.mark.parametrize("css_selector,value_format",
                         [("#price", r"\d+"),
                          (".price", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", None)])
def test_get_price_raise_price_not_found(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", mock_get)

    price_finder = PriceFinder()

    with pytest.raises(PriceNotFoundException):
        _ = price_finder.get_price("http://fake.com",
                                   css_selector,
                                   value_format)
