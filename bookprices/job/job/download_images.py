import logging
import traceback
from queue import Queue
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.job.service.argument_service import JobRunArgumentName, JobRunArgumentService
from bookprices.job.service.image_download import ImageDownloadService
from bookprices.job.shared.error_message import FAILED_TO_PARSE_ARGUMENTS
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.repository.unit_of_work import UnitOfWork


class DownloadAllMissingImagesForBooksJob(JobBase):
    """ Downloads images for new books. """

    books_batch_size: ClassVar[int] = 300
    min_image_sources_per_thread: ClassVar[int] = 5

    name: ClassVar[str] = "DownloadAllMissingImagesForBooksJob"

    def __init__(self, config: Config, unit_of_work: UnitOfWork, image_download_service: ImageDownloadService) -> None:
        super().__init__(config)
        self._unit_of_work = unit_of_work
        self._image_download_service = image_download_service
        self._image_source_queue = Queue()
        self._image_filenames = {}
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            book_ids_offset = 0
            while book_ids := self._list_book_ids_with_no_image(book_ids_offset, self.books_batch_size):
                self._logger.info(f"Found {len(book_ids)} books with no image")
                self._image_download_service.download_images_for_books(book_ids)
                book_ids_offset = book_ids[-1]

            self._logger.info("Done!")
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(exit_status=JobExitStatus.FAILURE, error=ex)

    def _list_book_ids_with_no_image(self, offset: int, limit: int) -> list[int]:
        with self._unit_of_work as uow:
            return uow.book_repository.list_books_ids_without_image(offset, limit)

class DownloadSelectedImagesForBooksJob(JobBase):
    """ Downloads images for selected new books. """

    name: ClassVar[str] = "DownloadSelectedImagesForBooksJob"

    def __init__(
            self,
            config: Config,
            argument_service: JobRunArgumentService,
            db: Database,
            download_image_service: ImageDownloadService) -> None:
        super().__init__(config)
        self._argument_service = argument_service
        self._db = db
        self._download_image_service = download_image_service
        self._logger = logging.getLogger(self.name)

    def start(self, **kwargs) -> JobResult:
        try:
            if not (book_ids := self._argument_service.parse_argument(JobRunArgumentName.BOOK_IDS, **kwargs)):
                self._logger.error(f"Failed to parse book ids for {self.name}!")
                return JobResult(JobExitStatus.FAILURE, error=ValueError(FAILED_TO_PARSE_ARGUMENTS))

            self._logger.info(f"Downloading images for books {book_ids}...")
            self._download_image_service.download_images_for_books(book_ids)
            self._logger.info(f"Finished downloading images for books {book_ids}!")

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(JobExitStatus.FAILURE, error=ex)