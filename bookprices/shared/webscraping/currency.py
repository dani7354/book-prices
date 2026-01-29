class CurrencyConverter:
    def __init__(self) -> None:
        self._exchange_rates_to_dkk: dict[str, float] = {
            "DKK": 1.0,
            "SEK": 0.7068,
            "NOK": 0.6652,
            "EUR": 7.4668,
            "USD": 6.2390,
        }

    def convert_to_dkk(self, amount: float, currency: str) -> float:
        if not (rate := self._exchange_rates_to_dkk.get(currency)):
            raise ValueError(f"Unsupported currency: {currency}")

        return round(amount * rate, 2)
