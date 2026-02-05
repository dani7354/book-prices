import pytest

from bookprices.shared.db.tables import Currency
from bookprices.shared.repository.currency import CurrencyRepository


@pytest.fixture
def currency_repository(data_session) -> CurrencyRepository:
    return CurrencyRepository(data_session)


def test_add_or_update_adds_currency(currency_repository: CurrencyRepository) -> None:
    currency = Currency(code="USD", rate_to_dkk=623.90, description="US Dollar")
    currency_repository.add_or_update_all([currency])
    currency_repository._session.commit()

    retrieved_currency = currency_repository.get_by_code("USD")

    assert retrieved_currency
    assert retrieved_currency.code == "USD"
    assert retrieved_currency.rate_to_dkk == 623.90
    assert retrieved_currency.description == "US Dollar"


def test_add_or_update_updates_exising_currencies(currency_repository: CurrencyRepository) -> None:
    usd_currency_code = "USD"
    currencies = [
        Currency(code=usd_currency_code, rate_to_dkk=623.90, description="US Dollar"),
        Currency(code="SEK", rate_to_dkk=70.10, description="Svenske kroner")
    ]
    currency_repository.add(currencies[0])
    currency_repository.add(currencies[1])
    currency_repository._session.commit()

    updated_currency = Currency(code=usd_currency_code, rate_to_dkk=666.66, description="US Dollar")
    currency_repository.add_or_update_all([updated_currency])

    retrieved_currency = currency_repository.get_by_code(usd_currency_code)

    assert retrieved_currency
    assert retrieved_currency.rate_to_dkk == 666.66
