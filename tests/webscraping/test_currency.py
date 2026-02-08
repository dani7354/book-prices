from datetime import datetime
import pytest

from bookprices.shared.api.currency import CurrencyApiClient
from bookprices.shared.db.tables import Currency
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.currency_service import CurrencyService
from bookprices.shared.webscraping.currency import CurrencyConverter


@pytest.fixture
def converter(session_factory) -> CurrencyConverter:
    unit_of_work = UnitOfWork(session_factory)
    with unit_of_work as uow:
        uow.currency_repository.add_or_update_all([
            Currency(code="DKK", description="Dansk krone", rate_to_dkk=100.0, updated=datetime.now()),
            Currency(code="SEK", description="Svensk krone", rate_to_dkk=70.68, updated=datetime.now()),
            Currency(code="NOK", description="Norsk krone", rate_to_dkk=66.52, updated=datetime.now()),
            Currency(code="EUR", description="Euro", rate_to_dkk=746.68, updated=datetime.now()),
            Currency(code="USD", description="US Dollar", rate_to_dkk=623.90, updated=datetime.now()),
        ])
    currency_service = CurrencyService(unit_of_work, CurrencyApiClient())
    return CurrencyConverter(currency_service)


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