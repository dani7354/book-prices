import logging
import os
from queue import Queue
from threading import Thread
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.model.book import Book
from bookprices.shared.webscraping.image import ImageDownloader, ImageSource, ImageNotDownloadedException


class DownloadImagesJob(JobBase):
    """ Downloads images for new books. """

    books_batch_size: ClassVar[int] = 300
    min_image_sources_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "DownloadImagesJob"

    def __init__(self, config: Config, db: Database, image_downloader: ImageDownloader) -> None:
        super().__init__(config)
        self._db = db
        self._image_downloader = image_downloader
        self._image_source_queue = Queue()
        self._image_filenames = {}
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            book_ids_offset, book_id_page = 0, 1
            while books := self._db.book_db.get_books_with_no_image(book_ids_offset, self.books_batch_size):
                self._logger.info(f"Found {len(books)} books with no image")
                self._download_images_for_books(books)
                book_id_page += 1
                book_ids_offset = (book_id_page - 1) * self.books_batch_size

            self._logger.info("Done!")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)

    def _download_images_for_books(self, books: list[Book]) -> None:
        self._logger.info(f"Loading image sources for {len(books)} books...")
        self._load_image_source_for_books(books)

        self._logger.info("Downloading images...")
        if self._image_source_queue.empty():
            self._logger.info("No image sources loaded!")
            return
        elif self._image_source_queue.qsize() / self._thread_count < self.min_image_sources_per_thread:
            self._logger.debug("Downloading images using single thread...")
            self._download_images()
        else:
            self._logger.debug(f"Downloading images using {self._thread_count} threads...")
            threads = []
            for _ in range(self._thread_count):
                t = Thread(target=self._download_images)
                threads.append(t)
                t.start()

            [t.join() for t in threads]

        if not self._image_filenames:
            self._logger.info("No images downloaded")
            return

        self._logger.info(f"Setting {len(self._image_filenames)} images on books...")
        for book_id, image in self._image_filenames.items():
            book = self._db.book_db.get_book(book_id)
            book.image_url = os.path.basename(image)
            self._db.book_db.update_book(book)

    def _load_image_source_for_books(self, books: list[Book]) -> None:
        book_stores_for_book = self._db.bookstore_db.get_bookstores_with_image_source_for_books(books)
        for book_id, book_in_book_stores in book_stores_for_book.items():
            bsb = book_in_book_stores[0]  # We only want one source, the first one is fine for now
            image_source = ImageSource(book_id, bsb.get_full_url(), bsb.book_store.image_css_selector, str(book_id))
            self._image_source_queue.put(image_source)

    def _download_images(self) -> None:
        while not self._image_source_queue.empty():
            image_source = self._image_source_queue.get()
            try:
                self._logger.debug(f"Downloading image for book with id {image_source.book_id}...")
                image = self._image_downloader.download_image(image_source)
                self._image_filenames[image_source.book_id] = image
            except ImageNotDownloadedException as ex:
                self._logger.error(ex)
