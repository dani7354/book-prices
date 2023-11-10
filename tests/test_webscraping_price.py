import pytest
import requests
import shared
from bookprices.shared.webscraping.price import (
    get_price,
    PriceSelectorError,
    PriceFormatError)


@pytest.mark.parametrize("css_selector,value_format",
                         [(".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+\.\d+")])
def test_get_price_value_without_currency(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", lambda url, allow_redirects: shared.create_fake_response("price_format.html"))

    price = get_price("https://fake.com", css_selector, value_format)

    assert price == 229.0


@pytest.mark.parametrize("css_selector,value_format",
                         [("#price", r"\d+"),
                          (".price", r"\d+")])
def test_get_price_raise_price_selector_error(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", lambda url, allow_redirects: shared.create_fake_response("price_format.html"))
    with pytest.raises(PriceSelectorError):
        _ = get_price("https://fake.com", css_selector, value_format)


@pytest.mark.parametrize("css_selector,value_format",
                         [(".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", None)])
def test_get_price_raise_price_format_error(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", lambda url, allow_redirects: shared.create_fake_response("price_format.html"))
    with pytest.raises(PriceFormatError):
        _ = get_price("https://fake.com", css_selector, value_format)
