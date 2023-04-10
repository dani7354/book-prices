#!/usr/bin/env python3
import logging
import shared
import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configuration.config import ConfigLoader
from data.bookprice_db import BookPriceDb
from book_source.image_downloader import ImageDownloader, ImageSource

MAX_THREAD_COUNT = 10
LOG_FILE_NAME = "download_images.log"


def get_books_without_image(books: list) -> list:
    books_without_image = []
    for b in books:
        if not b.image_url:
            books_without_image.append(b)

    return books_without_image


def get_image_source_for_books(book_stores_for_book: dict) -> list:
    image_source_for_books = []
    for book_id, book_in_book_stores in book_stores_for_book.items():
        for book_store_book in book_in_book_stores:
            if book_store_book.book_store.image_css_selector is not None:
                image_source_for_books.append(ImageSource(book_id,
                                                          book_store_book.get_full_url(),
                                                          book_store_book.book_store.image_css_selector,
                                                          str(book_id)))
                break

    return image_source_for_books


def run():
    args = shared.parse_arguments()
    configuration = ConfigLoader.load(args.configuration)
    shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)

    logging.info("Config loaded!")
    logging.info("Finding books with missing images...")
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    logging.debug("Getting books from db...")
    all_books = books_db.get_books()
    books_without_image = get_books_without_image(all_books)
    if len(books_without_image) == 0:
        logging.info("An image exists for each book.")
        sys.exit(0)

    logging.debug(f"Getting book stores for {len(books_without_image)} books...")
    book_stores_for_book = books_db.get_book_stores_for_books(books_without_image)

    logging.debug("Downloading images...")
    image_download_request = get_image_source_for_books(book_stores_for_book)
    image_downloader = ImageDownloader(max_thread_count=MAX_THREAD_COUNT, location=configuration.imgdir)
    downloaded_images = image_downloader.download_images(image_download_request)
    logging.debug(f"{len(downloaded_images)} images downloaded")

    logging.info(f"Updating image for {len(downloaded_images)}...")
    for book_id, image in downloaded_images.items():
        book = book_stores_for_book[book_id][0].book
        book.image_url = Path(image).name

        logging.debug(f"Setting image url {book.image_url} for book with id {book_id}")
        books_db.update_book(book)

    logging.info("Done!")


if __name__ == "__main__":
    run()
