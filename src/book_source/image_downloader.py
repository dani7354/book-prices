from bs4 import BeautifulSoup
from threading import Thread
from queue import Queue
import requests
import os


BS_HTML_PARSER = "html.parser"
HTML_SRC = "src"
FALLBACK_FILE_EXT = ".file"


class ImageSource:
    def __init__(self, id: int, page_url: str, image_css_selector: str, new_image_filename: str):
        self.id = id
        self.page_url = page_url
        self.image_css_selector = image_css_selector
        self.new_image_filename = new_image_filename


class ImageDownloader:
    file_extensions = {"image/jpg": ".jpg",
                       "image/jpeg": ".jpeg",
                       "image/png": ".png",
                       "image/bmp": ".bmp"}

    def __init__(self, max_thread_count: int, location: str):
        self.max_thread_count = max_thread_count
        self.location = location

    def download_images(self, image_sources: list) -> dict:
        image_source_queue = self._create_image_source_queue(image_sources)
        downloaded_images = {}
        threads = []
        for _ in range(self.max_thread_count):
            t = Thread(target=self._get_image_url_and_download, args=(image_source_queue, downloaded_images,))
            threads.append(t)
            t.start()

        [t.join() for t in threads]

        return downloaded_images

    def _get_image_url_and_download(self, image_source_queue: Queue, downloaded_images: dict):
        while not image_source_queue.empty():
            try:
                image_source = image_source_queue.get()
                image_url = self._get_image_url_from_page(image_source)
                if image_url is None:
                    continue

                image_filename = self._get_image(image_source.new_image_filename, image_url)
                if image_filename is not None:
                    downloaded_images[image_source.id] = image_filename
            except:
                continue

    @staticmethod
    def _get_image_url_from_page(image_source: ImageSource) -> str | None:
        page_response = requests.get(image_source.page_url)
        if page_response.status_code != 200:
            return None

        page_content_bs = BeautifulSoup(page_response.content.decode(), BS_HTML_PARSER)
        img_element = page_content_bs.select_one(image_source.image_css_selector)
        if img_element is None:
            return None

        return img_element[HTML_SRC]

    def _get_image(self, filename_base: str, url: str) -> str | None:
        image_response = requests.get(url)
        if image_response.status_code != 200:
            return None

        image_file_path = self._get_image_name(filename_base, self.location, image_response.headers)
        with open(image_file_path, "wb") as image:
            image.write(image_response.content)

        return image_file_path

    def _get_image_name(self, filename_base: str, location: str, headers) -> str:
        content_type = headers["Content-Type"]
        extension = self.file_extensions[content_type] if content_type in self.file_extensions else FALLBACK_FILE_EXT
        filename = f"{filename_base}{extension}"

        return os.path.join(location, filename)

    @staticmethod
    def _create_image_source_queue(image_sources: list) -> Queue:
        image_source_queue = Queue()
        for url in image_sources:
            image_source_queue.put(url)

        return image_source_queue
