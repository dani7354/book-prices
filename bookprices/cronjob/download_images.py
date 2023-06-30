#!/usr/bin/env python3
import logging
import os
import sys
from queue import Queue
from threading import Thread
from bookprices.cronjob import shared
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.model.book import Book
from bookprices.shared.webscraping.image import ImageDownloader, ImageSource

MAX_THREAD_COUNT = 10
LOG_FILE_NAME = "download_images.log"


class DownloadImagesJob:
    def __init__(self, db: Database,
                 image_downloader: ImageDownloader,
                 image_folder: str,
                 max_thread_count: int):
        self.db = db
        self.image_downloader = image_downloader
        self.image_folder = image_folder
        self.max_thread_count = max_thread_count
        self.image_source_queue = Queue()
        self.image_filenames = {}

    def run(self):
        logging.debug("Getting books with missing image...")
        books = self._get_books_without_image()
        if not books:
            logging.info("No books without image found")
            return

        logging.debug("Downloading image sources...")
        image_source_for_books = self._get_image_source_for_books(books)
        if not image_source_for_books:
            logging.info("No image sources found")
            return

        self._fill_queue(image_source_for_books)

        logging.debug("Downloading images...")
        threads = []
        for _ in range(self.max_thread_count):
            t = Thread(target=self._download_images)
            threads.append(t)
            t.start()

        [t.join() for t in threads]
        if not self.image_filenames:
            logging.info("No images downloaded")
            return

        logging.debug("Setting images on books...")
        for book_id, image in self.image_filenames.items():
            book = self.db.book_db.get_book(book_id)
            book.image_url = os.path.basename(image)
            self.db.book_db.update_book(book)

        logging.info("Done!")

    def _get_books_without_image(self) -> list[Book]:
        all_books = self.db.book_db.get_books()
        books_without_image = [b for b in all_books if not b.image_url]

        return books_without_image

    def _get_image_source_for_books(self, books: list[Book]) -> dict[int, ImageSource]:
        book_stores_for_book = self.db.bookstore_db.get_book_stores_for_books(books)
        image_source_for_books = {}
        for book_id, book_in_book_stores in book_stores_for_book.items():
            for bsb in book_in_book_stores:
                if book_id in image_source_for_books or bsb.book_store.image_css_selector is None:
                    break

                image_source_for_books[book_id] = ImageSource(book_id,
                                                              bsb.get_full_url(),
                                                              bsb.book_store.image_css_selector,
                                                              str(book_id))

        return image_source_for_books

    def _fill_queue(self, image_source_for_books: dict[int, ImageSource]):
        for image_source in image_source_for_books.values():
            self.image_source_queue.put(image_source)

    def _download_images(self):
        while not self.image_source_queue.empty():
            image_source = self.image_source_queue.get()
            try:
                image = self.image_downloader.download_image(image_source)
                self.image_filenames[image_source.book_id] = image
            except Exception as ex:
                logging.error(f"Error downloading image for book {image_source.book_id}: {ex}")
                continue


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        logging.info("Config loaded!")

        logging.info("Finding books with missing images...")
        db = Database(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

        image_downloader = ImageDownloader(configuration.imgdir)
        download_images_job = DownloadImagesJob(db, image_downloader, configuration.imgdir, MAX_THREAD_COUNT)
        download_images_job.run()
    except Exception as ex:
        logging.error(f"Error downloading images: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
