from bs4 import BeautifulSoup
import requests
import os
import bookprices.shared.webscraping.options as options

HTML_SRC = "src"
FALLBACK_FILE_EXT = ".file"


class ImageSource:
    def __init__(self, book_id: int, page_url: str, image_css_selector: str, new_image_filename: str):
        self.book_id = book_id
        self.page_url = page_url
        self.image_css_selector = image_css_selector
        self.new_image_filename = new_image_filename


class ImageDownloader:
    def __init__(self, location: str):
        self.location = location
        self.file_extensions = {"image/jpg": ".jpg",
                                "image/jpeg": ".jpeg",
                                "image/png": ".png",
                                "image/bmp": ".bmp"}

    def download_image(self, image_source: ImageSource) -> str:
        image_url = self._get_image_url_from_page(image_source)
        image_filename = self._get_image(image_source.new_image_filename, image_url)

        return image_filename

    def _get_image(self, filename_base: str, url: str) -> str:
        image_response = requests.get(url)
        image_response.raise_for_status()
        image_file_path = self._get_image_name(filename_base, self.location, image_response.headers)

        with open(image_file_path, "wb") as image:
            image.write(image_response.content)

        return image_file_path

    def _get_image_name(self, filename_base: str, location: str, headers) -> str:
        content_type = headers.get("Content-Type")
        extension = self.file_extensions.get(content_type, FALLBACK_FILE_EXT)
        filename = f"{filename_base}{extension}"

        return os.path.join(location, filename)

    @staticmethod
    def _get_image_url_from_page(image_source: ImageSource) -> str:
        page_response = requests.get(image_source.page_url)
        page_response.raise_for_status()
        page_content_bs = BeautifulSoup(page_response.content.decode(), options.BS_HTML_PARSER)
        img_element = page_content_bs.select_one(image_source.image_css_selector)

        return img_element.get(HTML_SRC)
