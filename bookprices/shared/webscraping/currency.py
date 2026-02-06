from bookprices.shared.service.currency_service import CurrencyService


class CurrencyConverter:
    def __init__(self, currency_service: CurrencyService) -> None:
        self._currency_service = currency_service

    def convert_to_dkk(self, amount: float, currency: str) -> float:
        if not (rate := self._currency_service.get_rate(currency)):
            raise ValueError(f"Unsupported currency: {currency}")

        return round(amount * rate, 2)
