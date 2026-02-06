import logging
from datetime import datetime

from bookprices.shared.api.currency import CurrencyApiClient
from bookprices.shared.db.tables import Currency
from bookprices.shared.repository.unit_of_work import UnitOfWork


class CurrencyService:

    def __init__(self, unit_of_work: UnitOfWork, api_client: CurrencyApiClient) -> None:
        self._unit_of_work = unit_of_work
        self._api_client = api_client

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_rate(self, currency_code: str) -> float | None:
        with self._unit_of_work as uow:
            if not (currency := uow.currency_repository.get_by_code(currency_code)):
                self._logger.warning(f"Currency with code {currency_code} not found.")
                return None

        return currency.rate_to_dkk

    def update_rates(self) -> None:
        self._logger.info("Updating currency rates...")
        currencies_to_update = self._api_client.get_exchange_rates()
        self._logger.info(f"Fetched {len(currencies_to_update)} currency rates from API.")

        updated_currency_entities = [
            Currency(
                code=currency.currency_code,
                description=currency.description,
                updated=datetime.now(),
                rate_to_dkk=currency.rate_to_dkk) for currency in currencies_to_update
        ]

        with self._unit_of_work as uow:
            uow.currency_repository.add_or_update_all(updated_currency_entities)
        self._logger.info("Currency rates updated successfully.")
