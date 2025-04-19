import logging
from queue import Queue
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.image_download import ImageDownloadService
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.webscraping.image import ImageDownloader


class DownloadImagesJob(JobBase):
    """ Downloads images for new books. """

    books_batch_size: ClassVar[int] = 300
    min_image_sources_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "DownloadImagesJob"

    def __init__(self, config: Config, db: Database, image_download_service: ImageDownloadService) -> None:
        super().__init__(config)
        self._db = db
        self._image_download_service = image_download_service
        self._image_source_queue = Queue()
        self._image_filenames = {}
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            book_ids_offset, book_id_page = 0, 1
            while book_ids := self._db.book_db.get_book_ids_with_no_image(book_ids_offset, self.books_batch_size):
                self._logger.info(f"Found {len(book_ids)} books with no image")
                self._image_download_service.download_images_for_books(book_ids)
                book_id_page += 1
                book_ids_offset = (book_id_page - 1) * self.books_batch_size

            self._logger.info("Done!")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)


class DownloadImagesForBooksJob(JobBase):
    """ Downloads images for selected new books. """

    name: ClassVar[str] = "DownloadImagesForBookJob"

    def __init__(self, config: Config, db: Database, download_image_service: ImageDownloadService) -> None:
        super().__init__(config)
        self._db = db
        self._download_image_service = download_image_service
        self._logger = logging.getLogger(self.name)


    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := [int(book_id) for book_id in kwargs.get("book_ids", [])]):
                self._logger.error("No valid book ids provided!")
                return JobResult(JobExitStatus.FAILURE)

            self._logger.info(f"Downloading images for books {book_ids}...")
            self._download_image_service.download_images_for_books(book_ids)
            self._logger.info(f"Finished downloading images for books {book_ids}!")

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            return JobResult(JobExitStatus.FAILURE, error_message=ex)