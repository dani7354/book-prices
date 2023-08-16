import pytest
import requests
import shared
from bookprices.shared.webscraping.price import PriceFinderStatic, PriceNotFoundException


@pytest.mark.parametrize("css_selector,value_format",
                         [(".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", r"\d+\.\d+")])
def test_get_price_value_without_currency(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", shared.mock_get_price)

    price_finder = PriceFinderStatic()
    price = price_finder.get_price("http://fake.com", css_selector, value_format)

    assert price == 229.0


@pytest.mark.parametrize("css_selector,value_format",
                         [("#price", r"\d+"),
                          (".price", r"\d+"),
                          (".table > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(2)", None),
                          (".table > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)", None)])
def test_get_price_raise_price_not_found(monkeypatch, css_selector, value_format):
    monkeypatch.setattr(requests, "get", shared.mock_get_price)

    price_finder = PriceFinderStatic()

    with pytest.raises(PriceNotFoundException):
        _ = price_finder.get_price("http://fake.com", css_selector, value_format)
