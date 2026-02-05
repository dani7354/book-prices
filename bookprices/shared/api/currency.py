import logging
from dataclasses import dataclass
from xml.etree import ElementTree

from bookprices.shared.webscraping.http import HttpClient, HttpResponse


class CurrencyApiUnavailableError(Exception):
    pass


class ResponseParsingError(Exception):
    pass


@dataclass(frozen=True)
class CurrencyExchangeRate:
    currency_code: str
    description: str
    rate_to_dkk: float


class CurrencyApiClient:
    """ API client for fetching currency exchange rates (to DKK) """
    _request_timeout_seconds = 10

    _xml_node_currency = "currency"
    _xml_attribute_rate = "rate"
    _xml_attribute_code = "code"
    _xml_attribute_description = "desc"

    def __init__(self) -> None:
        self._url = "https://www.nationalbanken.dk/api/currencyratesxml?lang=da"

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_exchange_rates(self) -> list[CurrencyExchangeRate]:
        api_response = self._get_rates_from_api()
        return self._parse_api_response(api_response.text)

    def _get_rates_from_api(self) -> HttpResponse:
        try:
            with HttpClient(timeout_seconds=self._request_timeout_seconds) as client:
                response = client.get(self._url)
                return response
        except Exception as e:
            raise CurrencyApiUnavailableError("Failed to fetch exchange rates from API") from e


    def _parse_api_response(self, response_content: str) -> list[CurrencyExchangeRate]:
        exchange_rates = []
        try:
            root = ElementTree.fromstring(response_content)
            for currency in root.findall(f".//{self._xml_node_currency}"):
                if not (code_attr := currency.attrib.get(self._xml_attribute_code)):
                    self._logger.warning(f"Currency node missing {self._xml_attribute_code} attribute. Skipping node.")
                    continue

                if not (description_attr := currency.attrib.get(self._xml_attribute_description)):
                    self._logger.warning(
                        f"Currency node missing {self._xml_attribute_description} attribute. Skipping node.")
                    continue

                if not (rate_attr := currency.attrib.get(self._xml_attribute_rate)):
                    self._logger.warning(
                        f"Currency node missing {self._xml_attribute_rate} attribute. Skipping node.")
                    continue

                code = code_attr
                description = description_attr
                rate = float(rate_attr.replace(",", "."))

                exchange_rates.append(
                    CurrencyExchangeRate(currency_code=code, rate_to_dkk=rate, description=description))

            if not exchange_rates:
                raise ResponseParsingError("No currency exchange rates parsed from response content")
        except (ElementTree.ParseError, ValueError) as e:
            raise ResponseParsingError("Failed to parse currency API response") from e

        return exchange_rates
