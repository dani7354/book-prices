#!/usr/bin/env python3
import shared
import logging
import sys
import os

from bookprices.shared.db.book import BookDb
from bookprices.shared.config import loader


DEFAULT_IMAGE_NAME = "default.png"
LOG_FILE_NAME = "delete_images.log"


def main():
    args = shared.parse_arguments()
    configuration = loader.load(args.configuration)
    shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)

    logging.info("Config loaded!")
    books_db = BookDb(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

    logging.info("Unused book images will now be deleted.")
    logging.info("Getting image file names from database...")
    all_books = books_db.get_books()
    image_filenames_db = [DEFAULT_IMAGE_NAME]
    for b in all_books:
        if b.image_url:
            image_filenames_db.append(b.image_url)

    if len(image_filenames_db) == 0:
        logging.info("No book images to check!")
        sys.exit(0)

    image_filenames_db = set(image_filenames_db)
    logging.debug(f"Got {len(image_filenames_db)} images!")

    image_files = set(os.listdir(configuration.imgdir))
    if len(image_files) == 0:
        logging.info("No image files in folder!")
        sys.exit(0)

    files_to_delete = image_files.difference(image_filenames_db)
    logging.info(f"{len(files_to_delete)} image files will be deleted.")

    for file in files_to_delete:
        file_path = os.path.join(configuration.imgdir, file)
        logging.debug(f"Deleting image file: {file_path}")
        os.remove(file_path)

    logging.info("Done!")


if __name__ == "__main__":
    main()
