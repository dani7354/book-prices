import logging
import os
from queue import Queue, Empty
from threading import Thread
from typing import ClassVar
from urllib.parse import urljoin

from bookprices.shared.db.tables import BookStoreBook, Book
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.webscraping.image import ImageDownloader, ImageSource, ImageNotDownloadedException


class ImageDownloadService:
    """ Service for downloading images for books. Used by image download jobs. """

    min_image_sources_per_thread: ClassVar[int] = 5

    def __init__(self, unit_of_work: UnitOfWork, image_downloader: ImageDownloader, thread_count: int) -> None:
        self._unit_of_work = unit_of_work
        self._image_downloader = image_downloader
        self._thread_count = thread_count
        self._image_source_queue: Queue[ImageSource] = Queue()
        self._image_filenames = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def download_images_for_books(self, book_ids: list[int]) -> None:
        self._logger.info(f"Loading books: {book_ids}")
        books = self._list_books(book_ids)
        
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
            with self._unit_of_work as uow:
                book = uow.book_repository.get_book(book_id)
                book.image_url = os.path.basename(image)
                uow.book_repository.update_book(book)

    def _list_books(self, book_ids: list[int]) -> list[Book]:
        with self._unit_of_work as uow:
            return uow.book_repository.list_by_id(book_ids)

    def _load_image_source_for_books(self, books: list[Book]) -> None:
        book_ids = [book.id for book in books]
        with self._unit_of_work as uow:
            book_stores_for_book = uow.bookstore_repository.get_bookstores_for_books(book_ids)

        for book_id, book_in_book_stores in book_stores_for_book.items():
            bsb = book_in_book_stores[0]  # We only want one source, the first one is fine for now
            image_source = ImageSource(book_id, self._format_url(bsb), bsb.book_store.image_css_selector, str(book_id))
            self._image_source_queue.put(image_source)

    def _download_images(self) -> None:
        while (image_source := self._get_next_enqueued_image_sources()) is not None:
            try:
                self._logger.debug(f"Downloading image for book with id {image_source.book_id}...")
                if not (image := self._image_downloader.download_image(image_source)):
                    continue
                self._image_filenames[image_source.book_id] = image
            except ImageNotDownloadedException as ex:
                self._logger.error(ex)

    def _get_next_enqueued_image_sources(self) -> ImageSource | None:
        try:
            return self._image_source_queue.get_nowait()
        except Empty:
            return None

    @staticmethod
    def _format_url(book_store_book: BookStoreBook) -> str:
        return urljoin(book_store_book.book_store.url, book_store_book.url)
