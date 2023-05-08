import requests
import options
from bs4 import BeautifulSoup


class BookFinder:
    HTML_HREF = "href"

    @classmethod
    def search_book_isbn(cls, search_url: str, book_isbn: str, match_url_css: str) -> str | None:
        url = search_url.format(book_isbn)
        match_url = cls._get_match_url(url, match_url_css)

        return match_url

    @classmethod
    def _get_match_url(cls, url: str, match_url_css: str | None) -> str | None:
        response = requests.get(url)
        if response.status_code > 399:
            return None

        if not match_url_css:
            if cls._was_redirected_to_detail_page(response):
                return response.url
            return None

        content_bs = BeautifulSoup(response.content.decode(), options.BS_HTML_PARSER)
        match_url_tag = content_bs.select_one(match_url_css)
        if match_url_tag is None:
            return None

        return match_url_tag[cls.HTML_HREF]

    @staticmethod
    def _was_redirected_to_detail_page(response: requests.Response):
        return len(response.history) > 0 and response.history[0].status_code in (301, 302)