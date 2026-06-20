import logging
import json
from abc import ABC, abstractmethod
from collections import Counter

from urllib.parse import urljoin, urlparse
from typing import ClassVar
from dataclasses import dataclass, replace
from bookprices.shared.webscraping.content import HtmlContent
from bookprices.shared.webscraping.http import HttpClient, HttpResponse, RateLimiter

REDIRECTED_PERMANENT = 301
REDIRECTED_TEMPORARY = 302


class BookNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class SearchResult:
    bookstore_id: int
    url: str | None
    success: bool = False


class BookScraper(ABC):
    """ Abstract base class for book scraper used for searching for books in a bookstore. """

    def __init__(self) -> None:
        """ Should not be instantiated directly. """
        pass

    @abstractmethod
    def find_book(self, isbn: str) -> SearchResult:
        raise NotImplementedError


class RedirectsToDetailPageBookScraper(BookScraper):
    """ Book scraper for bookstores that redirect to the book detail page on search. """
    _timeout_seconds: ClassVar[int] = 5

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            isbn_css_selector: str) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._isbn_css_selector = isbn_css_selector
        self._logger = logging.getLogger(self.__class__.__name__)

    def find_book(self, isbn: str) -> SearchResult:
        search_url = self._search_url.format(isbn)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(search_url)
            if response.redirected and self._is_match_url_valid(response.url, isbn):
                return SearchResult(bookstore_id=self._bookstore_id, url=response.url, success=True)

        return SearchResult(bookstore_id=self._bookstore_id, url=None, success=False)

    def _is_match_url_valid(
            self,
            match_url: str,
            isbn: str) -> bool:
        full_match_url = urljoin(self._bookstore_url, urlparse(match_url).path)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(full_match_url)

        if isbn in response.url:
            return True

        response_bs = HtmlContent(response.text)
        if not (isbn_element := response_bs.find_element_text_by_css(self._isbn_css_selector)):
            self._logger.error(
                f"No matches for ISBN CSS selector in the response body ({response.url, self._isbn_css_selector})")
            return False

        if isbn in str(isbn_element):
            return True

        return False


class RateLimitedRedirectsToDetailPageBookScraper(RedirectsToDetailPageBookScraper):
    """ Book scraper for bookstores that redirect to the book detail page on search with rate limiting. """

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            isbn_css_selector: str,
            max_requests: int,
            period_seconds: int) -> None:
        super().__init__(bookstore_id, bookstore_url, search_url, isbn_css_selector)
        self._rate_limiter = RateLimiter(max_requests, period_seconds)
        self._logger = logging.getLogger(self.__class__.__name__)

    def find_book(self, isbn: str) -> SearchResult:
        self._rate_limiter.wait_if_needed()
        return super().find_book(isbn)

    def _is_match_url_valid(self, match_url: str, isbn: str) -> bool:
        self._rate_limiter.wait_if_needed()
        return super()._is_match_url_valid(match_url, isbn)


class MatchesInResultListBookScraper(BookScraper):
    """ Book scraper for bookstores that list search results in a result list. """
    _timeout_seconds: ClassVar[int] = 5
    _href_tag : ClassVar[str] = "href"

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            search_result_css_selector: str,
            isbn_css_selector: str) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._search_result_css_selector = search_result_css_selector
        self._isbn_css_selector = isbn_css_selector
        self._logger = logging.getLogger(self.__class__.__name__)

        self._url_request_count = Counter()

    def find_book(self, isbn: str) -> SearchResult:
        search_url = self._search_url.format(isbn)
        search_result = SearchResult(bookstore_id=self._bookstore_id, success=False, url=None)
        with HttpClient(timeout_seconds=self._timeout_seconds) as http_client:
            response = http_client.get(search_url)
            if response.redirected:
                self._logger.warning(
                    f"This scraper {self.__class__.__name__} cannot handle redirects.")
                return search_result

            if not (match_url := self._get_match_url(response)):
                return search_result

            if self._is_match_url_valid(isbn, match_url):
                return replace(search_result, url=match_url, success=True)

        return search_result

    def _get_match_url(self, response: HttpResponse) -> str | None:
        content_bs = HtmlContent(response.text)
        if not (match_url := content_bs.find_element_and_get_attribute_value(
                self._search_result_css_selector, self._href_tag)):
            self._logger.error(
                f"Couldn't find match url in the search results ({response.url, self._search_result_css_selector}).")
            return None

        return match_url

    def  _is_match_url_valid(self, isbn: str, match_url: str) -> bool:
        with HttpClient() as http_client:
            full_url = urljoin(self._bookstore_url, urlparse(match_url).path)
            response = http_client.get(full_url)
            if response.redirected:
                self._logger.warning(f"Match URL {match_url} redirected to {response.url}.")

        content_bs = HtmlContent(response.text)
        if not (isbn_element := content_bs.find_element_text_by_css(self._isbn_css_selector)):
            self._logger.error(
                f"No matches for ISBN CSS selector in the response body ({response.url, self._isbn_css_selector})")
            return False

        return isbn in str(isbn_element)


class RateLimitedMatchesInResultListBookScraper(MatchesInResultListBookScraper):
    """ Book scraper for bookstores that list search results in a result list with rate limiting. """

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            search_result_css_selector: str,
            isbn_css_selector: str,
            max_requests: int,
            period_seconds: int) -> None:
        super().__init__(
            bookstore_id,
            bookstore_url,
            search_url,
            search_result_css_selector,
            isbn_css_selector)
        self._rate_limiter = RateLimiter(max_requests, period_seconds)
        self._logger = logging.getLogger(self.__class__.__name__)

    def find_book(self, isbn: str) -> SearchResult:
        self._rate_limiter.wait_if_needed()
        return super().find_book(isbn)

    def _is_match_url_valid(self, isbn: str, match_url: str) -> bool:
        self._rate_limiter.wait_if_needed()
        return super()._is_match_url_valid(isbn, match_url)


class PlusbogBookScraper(BookScraper):

    _min_html_response_length: ClassVar[int] = 8

    _headers_for_search: ClassVar[dict[str, str]] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            search_result_css_selector: str,
            rate_limiter: RateLimiter) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._search_result_css_selector = search_result_css_selector
        self._rate_limiter = rate_limiter

        self._logger = logging.getLogger(self.__class__.__name__)

    def find_book(self, isbn: str) -> SearchResult:
        self._rate_limiter.wait_if_needed()
        response = self._post_search(isbn)

        search_result = SearchResult(bookstore_id=self._bookstore_id, url=None, success=False)
        if not (match_url := self._parse_match_url(response)):
            return search_result

        if not self._is_match_url_valid(match_url, isbn):
            return search_result

        return replace(search_result, url=urljoin(self._bookstore_url, match_url), success=True)

    def _post_search(self, isbn: str) -> HttpResponse:
        with HttpClient(headers=self._headers_for_search) as http_client:
            response = http_client.post(self._search_url, self._create_form_data(isbn))
            return response

    def _parse_match_url(self, response: HttpResponse) -> str | None:
        response_json = json.loads(response.text)
        html_str = response_json.get("products", "")
        if len(html_str) < self._min_html_response_length:
            self._logger.debug("No match found in response JSON products field.")
            return None

        html_content = HtmlContent(html_str)
        if not (match_url := html_content.find_element_and_get_attribute_value(
                self._search_result_css_selector, "href")):
            self._logger.debug("Match url not found in HTML.")
            return None

        self._logger.debug(f"Found match url: {match_url}")
        return urlparse(match_url).path

    @staticmethod
    def _is_match_url_valid(match_url: str, isbn: str) -> bool:
        return match_url.endswith(isbn)

    @staticmethod
    def _create_form_data(isbn: str) -> dict[str, str | int]:
        return {
            "input": isbn,
            "pageIndex": 0,
            "isInitialPage": "false",
            "filtersPreExists": "true",
            "needAutoScroll": "false"
        }


class BogOgIdeBookScraper(BookScraper):
    """ Custom book scraper for store. Uses POST request to external API. """
    _json_responses_key: ClassVar[str] = "responses"
    _json_results_key: ClassVar[str] = "results"
    _json_product_id_key: ClassVar[str] = "productId"
    _json_shopify_handle_key: ClassVar[str] = "bogogide.myshopify.com_ShopifyHandle"
    _json_data_key: ClassVar[str] = "data"
    _json_value_key: ClassVar[str] = "value"

    _products_url_part: ClassVar[str] = "products"

    def __init__(
            self,
            bookstore_id: int,
            bookstore_url: str,
            search_url: str,
            search_result_css_selector: str,
            api_key: str,
            rate_limiter: RateLimiter) -> None:
        super().__init__()
        self._bookstore_id = bookstore_id
        self._bookstore_url = bookstore_url
        self._search_url = search_url
        self._search_result_css_selector = search_result_css_selector
        self._rate_limiter = rate_limiter
        self._logger = logging.getLogger(self.__class__.__name__)

        self._headers_for_search = {
            "Accept": "*/*",
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Origin": bookstore_url,
            "Referer": bookstore_url,
            "Sec-CH-UA-Platform": "Linux",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Sec-GPC": "1",
            "X-Relewise-Version": "client@2.23.1"
        }

    def find_book(self, isbn: str) -> SearchResult:
        self._rate_limiter.wait_if_needed()
        response = self._send_post(isbn)

        search_result = SearchResult(bookstore_id=self._bookstore_id, url=None, success=False)
        if not (match_url := self._parse_match_url(response, isbn)):
            return search_result

        if not self._is_match_url_valid(match_url, isbn):
            return search_result

        return replace(search_result, url=match_url, success=True)

    def _send_post(self, isbn: str):
        with HttpClient(headers=self._headers_for_search) as http_client:
            response = http_client.post(self._search_url, payload=self._create_json_payload(isbn))
            self._logger.debug(f"Sent POST request to {self._search_url} with payload for ISBN {isbn}. Response status code: {response.status_code}")
            return response

    def _parse_match_url(self, response: HttpResponse, isbn: str) -> str | None:
        response_json = json.loads(response.text)
        for search_response in response_json.get(self._json_responses_key, []):
            if not (search_results := search_response.get(self._json_results_key)):
                self._logger.debug("Key %s not found in response!", self._json_results_key)
                return None

            for result in search_results:
                if not (data_obj := result.get(self._json_data_key)):
                    continue

                if shopify_handle_obj := data_obj.get(self._json_shopify_handle_key):
                    book_url = shopify_handle_obj[self._json_value_key]
                    match_url = f"/{self._products_url_part}/{book_url}"
                    self._logger.debug(f"Found match url for book %s in bookstore %s", isbn, match_url)
                    return urljoin(self._bookstore_url, match_url)

        return None

    @staticmethod
    def _is_match_url_valid(match_url: str, isbn: str) -> bool:
        with HttpClient() as http_client:
            response = http_client.get(match_url)
            html_content = HtmlContent(response.text)

            return html_content.contains_text(isbn)

    @staticmethod
    def _create_json_payload(isbn: str) ->  str:
        payload = {
        "$type": "Relewise.Client.Requests.Search.SearchRequestCollection, Relewise.Client",
          "currency": {
            "value": "DKK"
          },
          "language": {
            "value": "da"
          },
          "displayedAtLocation": "Search page",
          "user": {
            "Classifications": {
              "Country": "DK"
            },
            "Identifiers": {},
            "Data": {}
          },
          "filters": None,
          "postFilters": None,
          "relevanceModifiers": None,
          "requests": [
            {
              "$type": "Relewise.Client.Requests.Search.ProductSearchRequest, Relewise.Client",
              "currency": {
                "value": "DKK"
              },
              "language": {
                "value": "da"
              },
              "displayedAtLocation": "Search page",
              "user": {
                "Classifications": {
                  "Country": "DK"
                },
                "Identifiers": {},
                "Data": {}
              },
              "filters": None,
              "postFilters": None,
              "relevanceModifiers": None,
              "take": 24,
              "skip": 0,
              "term": isbn,
              "facets": {
                "items": [
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.number_of_participants",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.age",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.publisher",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.series_name_reference",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.author",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.brand",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.PriceRangeFacet, Relewise.Client",
                    "field": "SalesPrice",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.global_binding",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.language",
                    "selected": None
                  },
                  {
                    "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.ProductDataStringValueFacet, Relewise.Client",
                    "field": "Data",
                    "key": "bogogide.myshopify.com_pim.purchasing_group",
                    "selected": None
                  }
                ],
                "$type": "Relewise.Client.DataTypes.Search.Facets.Queries.FacetQuery, Relewise.Client"
              },
              "settings": {
                "$type": "Relewise.Client.Requests.Search.Settings.ProductSearchSettings, Relewise.Client",
                "recommendations": {},
                "selectedProductProperties": {
                  "displayName": "true",
                  "dataKeys": [
                    "IsAvailable",
                    "Tags",
                    "bogogide.myshopify.com_ShopifyHandle",
                    "bogogide.myshopify.com_ImageUrls",
                    "bogogide.myshopify.com_pim.author",
                    "bogogide.myshopify.com_pim.global_binding",
                    "bogogide.myshopify.com_pim.language",
                    "bogogide.myshopify.com_pim.badges",
                    "bogogide.myshopify.com_pim.book",
                    "bogogide.myshopify.com_custom.kobslogik",
                    "bogogide.myshopify.com_judgeme.review_widget_data"
                  ],
                  "pricing": "true"
                },
                "selectedVariantProperties": {
                  "dataKeys": [
                    "bogogide.myshopify.com_ShopifyVariantId"
                  ]
                },
                "explodedVariants": 1
              },
              "sorting": None,
              "retailMedia": None
            }
          ]
        }

        return json.dumps(payload)
