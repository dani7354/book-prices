from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
from urllib.parse import urlparse, urljoin
import os
import bookprices.shared.webscraping.options as options

HTML_SRC = "src"


class ImageNotDownloadedException(Exception):
    pass


class ImageSource:
    def __init__(self, book_id: int, page_url: str, image_css_selector: str, new_image_filename: str):
        self.book_id = book_id
        self.page_url = page_url
        self.image_css_selector = image_css_selector
        self.new_image_filename = new_image_filename

    def get_base_url(self) -> str:
        parsed_url = urlparse(self.page_url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"


class ImageDownloader:
    def __init__(self, location: str):
        self._location = location
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
            image_file_path = self._get_image_name(filename_base, self._location, image_response.headers)

            with open(image_file_path, "wb") as image:
                image.write(image_response.content)
        except HTTPError as ex:
            raise ImageNotDownloadedException(f"Failed to download image from {url}: {ex}")

        return image_file_path

    def _get_image_name(self, filename_base: str, location: str, headers) -> str:
        try:
            content_type = headers["Content-Type"]
            extension = self._file_extensions[content_type]
            filename = f"{filename_base}{extension}"
        except KeyError as ex:
            raise ImageNotDownloadedException(f"Image format not supported: {ex}")

        return os.path.join(location, filename)

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
            url = img_element[HTML_SRC]
        except HTTPError as ex:
            raise ImageNotDownloadedException(f"Failed to connect to {image_source.page_url}: {ex}")
        except KeyError as ex:
            raise ImageNotDownloadedException(f"Failed to parse url from HTML element {image_source.image_css_selector}: "
                                              f"{ex}")

        return url
