import logging
import traceback
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.shared.db.tables import Book
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.book_image_file_service import BookImageFileService


DEFAULT_FALLBACK_IMAGE_NAME: str = "default.png"


class DeleteUnusedImagesJob(JobBase):
    """ Deletes image files that are no longer used by books on the site. """

    name: ClassVar[str] = "DeleteUnusedImagesJob"
    default_image_name: str = DEFAULT_FALLBACK_IMAGE_NAME

    def __init__(self, config: Config, db: Database, book_image_file_service: BookImageFileService) -> None:
        super().__init__(config)
        self.db = db
        self.image_folder = config.imgdir
        self._book_image_file_service = book_image_file_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self, *args, **kwargs) -> JobResult:
        try:
            if not (images_from_db := self._get_image_filenames_from_db()):
                self._logger.info("No book images to check!")
                return JobResult(JobExitStatus.SUCCESS)

            if not (images_from_folder := self._get_image_filenames_from_folder()):
                self._logger.info("No image files in folder!")
                return JobResult(JobExitStatus.SUCCESS)

            if not (images_to_delete := images_from_folder.difference(images_from_db)):
                self._logger.info("No image files to delete!")
                return JobResult(JobExitStatus.SUCCESS)

            self._logger.info(f"{len(images_to_delete)} image files will be deleted.")
            self._delete_files(images_to_delete)

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            self._logger.error(traceback.format_exc())
            return JobResult(JobExitStatus.FAILURE, error=ex)

    def _get_image_filenames_from_db(self) -> set[str]:
        self._logger.info("Getting image filenames from database...")
        image_filenames = set(self.db.book_db.get_book_image_urls())
        image_filenames.add(self.default_image_name)

        return image_filenames

    def _get_image_filenames_from_folder(self) -> set[str]:
        self._logger.info(f"Listing image filenames from folder {self.image_folder}...")
        return set(self._book_image_file_service.get_images_available())

    def _delete_files(self, files: set[str]) -> None:
        for file in files:
            try:
                if file.startswith('.'):
                    self._logger.info(f"Skipping hidden file {file}")
                    continue
                self._book_image_file_service.delete_image(file)
            except FileNotFoundError as ex:
                self._logger.error(f"{file} was not found in {self.image_folder}")
                self._logger.error(ex)


class DeleteExcludedBookImagesJob(JobBase):
    """ Job for deleting images that are excluded, in most cases temporary and default images. """

    name: ClassVar[str] = "DeleteExcludedBookImagesJob"
    default_image_name: ClassVar[str] = DEFAULT_FALLBACK_IMAGE_NAME
    book_batch_size: ClassVar[int] = 500

    def __init__(
            self,
            config: Config,
            unit_of_work: UnitOfWork,
            book_image_file_service: BookImageFileService) -> None:
        super().__init__(config)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._unit_of_work = unit_of_work
        self._book_image_file_service = book_image_file_service

    def start(self, **kwargs) -> JobResult:
        try:
            self.delete_excluded_images()
            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.exception(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error=ex)

    def delete_excluded_images(self) -> None:
        self._logger.info("Deleting excluded book images...")
        total_deleted, offset_book_id, page_count = 0, 0, 1
        while books := self._list_books_with_image(offset_book_id, self.book_batch_size):
            with self._unit_of_work as uow:
                self._logger.debug(f"Processing page {page_count} with {len(books)} books...")
                total_deleted += self._delete_excluded_images_batch(uow, books)
                self._logger.info(f"Processed page {page_count} ({len(books)} books)")

            offset_book_id = books[-1].id
            page_count += 1

        self._logger.info(f"Total excluded images deleted: {total_deleted}")

    def _delete_excluded_images_batch(self, uow: UnitOfWork, books: list[Book]) -> int:
        excluded_image_hashes = self._get_excluded_image_hashes()
        delete_count = 0
        for book in books:
            if not book.image_url:
                self._logger.warning(f"Book with id {book.id} not found or has no image, skipping...")
                continue

            image_hash = self._book_image_file_service.get_image_hash(book.image_url)
            if image_hash in excluded_image_hashes and book.image_url != self.default_image_name:
                self._logger.info(f"Deleting excluded image {book.image_url} for book with id {book.id}...")
                self._delete_image_for_book(uow, book)
                delete_count += 1

        return delete_count

    def _list_books_with_image(self, offset_book_id: int, limit: int) -> list[Book]:
        with self._unit_of_work as uow:
            books = uow.book_repository.list_books_with_image(offset_book_id, limit)

        return books

    def _get_excluded_image_hashes(self) -> set[str]:
        with self._unit_of_work as uow:
            excluded_images = uow.excluded_book_image_repository.list_excluded_images()

        return {excluded_image.hash for excluded_image in excluded_images}

    def _delete_image_for_book(self, uow: UnitOfWork, book: Book) -> None:
        self._logger.info(f"Deleting image {book.image_url}...")
        self._book_image_file_service.delete_image(book.image_url)
        book.image_url = None
        uow.book_repository.update(book)
