import pytest

from bookprices.shared.webscraping.currency import CurrencyConverter


@pytest.fixture
def converter() -> CurrencyConverter:
    return CurrencyConverter()


def test_currency_converter_converts_successfully_to_dkk(converter: CurrencyConverter) -> None:
    assert converter.convert_to_dkk(100, "DKK") == 100.0
    assert converter.convert_to_dkk(100, "SEK") == 70.68
    assert converter.convert_to_dkk(100, "NOK") == 66.52
    assert converter.convert_to_dkk(100, "EUR") == 746.68
    assert converter.convert_to_dkk(100, "USD") == 623.90


def test_currency_converter_raises_value_error_for_unsupported_currency(converter: CurrencyConverter) -> None:
    currency = "GBP"
    try:
        converter.convert_to_dkk(100, currency)
    except ValueError as e:
        assert str(e) == f"Unsupported currency: {currency}"
    else:
        assert False, "Expected ValueError for unsupported currency"