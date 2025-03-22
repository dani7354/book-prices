import logging
import os
from bookprices.job.job.base import JobBase
from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database


class DeleteImagesJob(JobBase):
    """ Deletes image files that are no longer used by books on the site. """

    default_image_name: str = "default.png"

    def __init__(self, config: Config, db: Database) -> None:
        super().__init__(config)
        self.db = db
        self.image_folder = config.imgdir
        self._logger = logging.getLogger(self.name)

    def start(self, *args, **kwargs) -> None:
        if not (images_from_db := self._get_image_filenames_from_db()):
            self._logger.info("No book images to check!")
            return

        if not (images_from_folder := self._get_image_filenames_from_folder()):
            self._logger.info("No image files in folder!")
            return

        if not (images_to_delete := images_from_folder.difference(images_from_db)):
            self._logger.info("No image files to delete!")
            return

        logging.info(f"{len(images_to_delete)} image files will be deleted.")
        self._delete_files(images_to_delete)

    def _get_image_filenames_from_db(self) -> set[str]:
        self._logger.info("Getting image filenames from database...")
        image_filenames = set(self.db.book_db.get_book_image_urls())
        image_filenames.add(self.default_image_name)

        return image_filenames

    def _get_image_filenames_from_folder(self) -> set[str]:
        self._logger.info(f"Listing image filenames from folder {self.image_folder}...")
        return set(os.listdir(self.image_folder))

    def _delete_files(self, files: set):
        for file in files:
            try:
                os.remove(os.path.join(self.image_folder, file))
            except FileNotFoundError as ex:
                logging.error(f"{file} blev ikke fundet i {self.image_folder}")
                logging.error(ex)
