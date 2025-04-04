import logging
import os
from typing import ClassVar

from bookprices.job.job.base import JobBase, JobResult, JobExitStatus
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database


class DeleteImagesJob(JobBase):
    """ Deletes image files that are no longer used by books on the site. """

    name: ClassVar[str] = "DeleteImagesJob"
    default_image_name: str = "default.png"

    def __init__(self, config: Config, db: Database) -> None:
        super().__init__(config)
        self.db = db
        self.image_folder = config.imgdir
        self._logger = logging.getLogger(self.name)

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

            logging.info(f"{len(images_to_delete)} image files will be deleted.")
            self._delete_files(images_to_delete)

            return JobResult(JobExitStatus.SUCCESS)
        except Exception as ex:
            self._logger.error(f"Unexpected error: {ex}")
            return JobResult(JobExitStatus.FAILURE, error_message=ex)

    def _get_image_filenames_from_db(self) -> set[str]:
        self._logger.info("Getting image filenames from database...")
        image_filenames = set(self.db.book_db.get_book_image_urls())
        image_filenames.add(self.default_image_name)

        return image_filenames

    def _get_image_filenames_from_folder(self) -> set[str]:
        self._logger.info(f"Listing image filenames from folder {self.image_folder}...")
        return set(os.listdir(self.image_folder))

    def _delete_files(self, files: set[str]) -> None:
        for file in files:
            try:
                if file.startswith('.'):
                    self._logger.info(f"Skipping hidden file {file}")
                    continue
                os.remove(os.path.join(self.image_folder, file))
            except FileNotFoundError as ex:
                logging.error(f"{file} blev ikke fundet i {self.image_folder}")
                logging.error(ex)
