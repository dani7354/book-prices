import logging

import requests
import bookprices.shared.webscraping.options as options
from typing import Mapping
from bs4 import BeautifulSoup
from dataclasses import dataclass
from requests.exceptions import HTTPError
from urllib.parse import urlparse, urljoin

from bookprices.shared.repository.unit_of_work import UnitOfWork
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

    def __init__(
            self,
            book_image_file_service: BookImageFileService,
            unit_of_work: UnitOfWork,
            location: str):
        self._location = location
        self._book_image_file_service = book_image_file_service
        self._unit_of_work = unit_of_work
        self._logger = logging.getLogger(self.__class__.__name__)
        self._file_extensions = {"image/jpg": ".jpg",
                                 "image/jpeg": ".jpeg",
                                 "image/png": ".png",
                                 "image/bmp": ".bmp"}

    def download_image(self, image_source: ImageSource) -> str | None:
        try:
            image_url = self._get_image_url_from_page(image_source)
            valid_url = self._get_valid_url(image_url, image_source)
            image_bytes, headers = self._get_image_from_url(valid_url)

            if not self._image_not_excluded(image_bytes):
                self._logger.warning(f"Image for book with id {image_source.book_id} is excluded, skipping...")
                return None

            image_filename = self._get_image_name(image_source.new_image_filename, headers)
            self._book_image_file_service.save_image(image_filename, image_bytes)

            return image_filename
        except FileExistsError as ex:
            self._logger.warning(f"Image already exists: {ex}")

    def _image_not_excluded(self, image_bytes: bytes) -> bool:
        image_hash = self._book_image_file_service.get_image_hash_from_bytes(image_bytes)
        with self._unit_of_work as uow:
            return not uow.excluded_book_image_repository.is_book_image_excluded(image_hash)

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

    @staticmethod
    def _get_image_from_url(url: str) -> tuple[bytes, dict[str, str]]:
        try:
            image_response = requests.get(url)
            image_response.raise_for_status()
            return image_response.content, dict(image_response.headers)
        except HTTPError as ex:
            raise ImageNotDownloadedException(f"Failed to download image from {url}: {ex}")