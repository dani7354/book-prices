import pytest
import requests
import shared
from unittest.mock import MagicMock
from bookprices.shared.webscraping.image import ImageDownloader, ImageSource


@pytest.mark.parametrize("css_selector,expected_url_found",
                         [("#img-folder-only", "https://example.com/static/images/books/1.jpg"),
                          ("#img-full-url", "https://example.com/static/images/books/1.jpg")])
def test_image_downloader_finds_url_from_img_element(monkeypatch, css_selector, expected_url_found):
    book_id = 1
    monkeypatch.setattr(requests, "get", lambda x: shared.create_fake_response("image.html"))
    image_downloader = ImageDownloader(".")
    image_downloader._get_image = MagicMock(return_value=f"{book_id}.jpg")
    image_source = ImageSource(book_id, "https://example.com/book1", css_selector, str(book_id))

    _ = image_downloader.download_image(image_source)

    image_downloader._get_image.assert_called_once_with(str(book_id), expected_url_found)
