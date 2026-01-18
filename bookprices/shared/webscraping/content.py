from typing import ClassVar

from bs4 import BeautifulSoup


class HtmlContent:
    _html_parser: ClassVar[str] = "html.parser"

    def __init__(self, html_content):
        self._html_content_bs = BeautifulSoup(html_content, self._html_parser)

    def find_element_text_by_css(self, css_selector: str) -> str | None:
        match = self._html_content_bs.select_one(css_selector)
        return match.get_text() if match else None

    def find_element_and_get_attribute_value(self, css_selector: str, attribute_name: str) -> str | None:
        match = self._html_content_bs.select_one(css_selector)
        return match.get(attribute_name) if match and match.has_attr(attribute_name) else None

    def contains_text(self, text: str) -> bool:
        return text.lower() in self._html_content_bs.text.lower()
