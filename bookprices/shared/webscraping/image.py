import requests
import bookprices.shared.webscraping.options as options
from typing import Mapping
from bs4 import BeautifulSoup
from dataclasses import dataclass
from requests.exceptions import HTTPError
from urllib.parse import urlparse, urljoin
from bookprices.shared.service.book_image_file_service import BookImageFileService


HTML_SRC = "src"


class ImageNotDownloadedException(Exception):
    pass


@dataclass(frozen=True)
class ImageSource:
    book_id: int
    page_url: str
    image_css_selector: str
    new_image_filename: str

    def get_base_url(self) -> str:
        parsed_url = urlparse(self.page_url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"


class ImageDownloader:
    def __init__(self, book_image_file_service: BookImageFileService, location: str):
        self._location = location
        self._book_image_file_service = book_image_file_service
        self._file_extensions = {"image/jpg": ".jpg",
                                 "image/jpeg": ".jpeg",
                                 "image/png": ".png",
                                 "image/bmp": ".bmp"}

    def download_image(self, image_source: ImageSource) -> str:
        image_url = self._get_image_url_from_page(image_source)
        valid_url = self._get_valid_url(image_url, image_source)
        image_filename = self._get_image(image_source.new_image_filename, valid_url)

        return image_filename

    def _get_image(self, filename_base: str, url: str) -> str:
        try:
            image_response = requests.get(url)
            image_response.raise_for_status()
            image_file_name = self._get_image_name(filename_base, image_response.headers)
            self._book_image_file_service.save_image(image_file_name, image_response.content)
        except HTTPError as ex:
            raise ImageNotDownloadedException(f"Failed to download image from {url}: {ex}")

        return image_file_name

    def _get_image_name(self, filename_base: str, headers: Mapping[str, str]) -> str:
        try:
            content_type = headers["Content-Type"]
            extension = self._file_extensions[content_type]
            return f"{filename_base}{extension}"
        except KeyError as ex:
            raise ImageNotDownloadedException(f"Image format not supported: {ex}")

    @staticmethod
    def _get_valid_url(url: str, image_source: ImageSource) -> str:
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return urljoin(image_source.get_base_url(), url)
        if not parsed_url.scheme:
            scheme = urlparse(image_source.get_base_url()).scheme
            return urljoin(f"{scheme}://", url)

        return url

    @staticmethod
    def _get_image_url_from_page(image_source: ImageSource) -> str:
        try:
            page_response = requests.get(image_source.page_url)
            page_response.raise_for_status()
            page_content_bs = BeautifulSoup(page_response.content.decode(), options.BS_HTML_PARSER)
            img_element = page_content_bs.select_one(image_source.image_css_selector)
            image_url = img_element[HTML_SRC]
            return image_url
        except HTTPError as ex:
            raise ImageNotDownloadedException(f"Failed to connect to {image_source.page_url}: {ex}")
        except KeyError as ex:
            raise ImageNotDownloadedException(f"Failed to parse url from HTML element {image_source.image_css_selector}: "
                                              f"{ex}")