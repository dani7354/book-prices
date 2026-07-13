import logging
import traceback
from queue import Queue
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.enum import JobRunArgumentName
from bookprices.job.service.image_download import ImageDownloadService
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database


class DownloadAllMissingImagesForBooksJob(JobBase):
    """ Downloads images for new books. """

    books_batch_size: ClassVar[int] = 300
    min_image_sources_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "DownloadAllMissingImagesForBooksJob"

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
            self._logger.error(traceback.format_exc())
            return JobResult(exit_status=JobExitStatus.FAILURE, error_message=ex)


class DownloadSelectedImagesForBooksJob(JobBase):
    """ Downloads images for selected new books. """

    name: ClassVar[str] = "DownloadSelectedImagesForBooksJob"

    def __init__(self, config: Config, db: Database, download_image_service: ImageDownloadService) -> None:
        super().__init__(config)
        self._db = db
        self._download_image_service = download_image_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := kwargs.get(JobRunArgumentName.BOOK_IDS)):
                self._logger.error(f"No book ids given for {self.name}!")
                return JobResult(JobExitStatus.FAILURE, error_message=ValueError("No book ids given!"))

            if not (isinstance(book_ids, list)) or not all(isinstance(book_id, int) for book_id in book_ids):
                self._logger.error("Invalid arguments: book_ids is not a list of integers!")
                return JobResult(
                    exit_status=JobExitStatus.FAILURE,
                    error_message=ValueError(f"Invalid argument type for {JobRunArgumentName.BOOK_IDS}"))

            self._logger.info(f"Downloading images for books {book_ids}...")
            self._download_image_service.download_images_for_books(book_ids)
            self._logger.info(f"Finished downloading images for books {book_ids}!")

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(JobExitStatus.FAILURE, error_message=ex)