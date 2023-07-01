#!/usr/bin/env python3
import logging
import os
import sys
from bookprices.cronjob import shared
from bookprices.shared.db.database import Database
from bookprices.shared.db.book import BookDb
from bookprices.shared.config import loader


DEFAULT_IMAGE_NAME = "default.png"
LOG_FILE_NAME = "delete_images.log"


class DeleteImagesJob:
    def __init__(self, books_db: BookDb, image_folder: str):
        self.books_db = books_db
        self.image_folder = image_folder

    def run(self):
        images_from_db = self._get_image_filenames_from_db()
        if not images_from_db:
            logging.info("No book images to check!")
            return

        images_from_folder = self._get_image_filenames_from_folder()
        if not images_from_folder:
            logging.info("No image files in folder!")
            return

        images_to_delete = images_from_folder.difference(images_from_db)
        if not images_to_delete:
            logging.info("No image files to delete!")
            return

        logging.info(f"{len(images_to_delete)} image files will be deleted.")
        self._delete_files(images_to_delete)

    def _get_image_filenames_from_db(self) -> set[str]:
        filenames = [b.image_url for b in self.books_db.get_books() if b.image_url]
        filenames.append(DEFAULT_IMAGE_NAME)

        return set(filenames)

    def _get_image_filenames_from_folder(self) -> set[str]:
        return set(os.listdir(self.image_folder))

    def _delete_files(self, files: set):
        for file in files:
            try:
                os.remove(os.path.join(self.image_folder, file))
            except FileNotFoundError as ex:
                logging.error(f"{file} blev ikke fundet i {self.image_folder}")
                logging.error(ex)


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        logging.info("Config loaded!")

        books_db = Database(configuration.database.db_host,
                            configuration.database.db_port,
                            configuration.database.db_user,
                            configuration.database.db_password,
                            configuration.database.db_name)

        delete_images_job = DeleteImagesJob(books_db.book_db, configuration.imgdir)
        delete_images_job.run()
    except Exception as ex:
        logging.error(f"Failed to delete images: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
