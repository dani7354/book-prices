#!/usr/bin/env python3
import argparse
import logging
from datetime import datetime
from queue import Queue
from threading import Thread
from configuration.config import ConfigLoader
from data.bookprice_db import BookPriceDb
from data.model import BookPrice
from book_source.web import WebshopPriceFinder

MAX_THREAD_COUNT = 8


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def setup_logging(logfile, loglevel):
    loglevel = loglevel
    logging.basicConfig(
        filename=logfile,
        filemode="a",
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=loglevel)
    logging.getLogger().addHandler(logging.StreamHandler())


def create_book_store_queue(book_stores_by_book_id) -> Queue:
    queue = Queue()
    for b in book_stores_by_book_id.values():
        queue.put(b)

    return queue


def get_updated_prices_for_book(book_stores) -> list:
    new_prices = []
    for book_in_store in book_stores:
        full_url = book_in_store.get_full_url()
        try:
            logging.debug(f"Getting price for book ID {book_in_store.book.id} at book store ID "
                          f"{book_in_store.book_store.id} (URL {full_url})")

            new_price_value = WebshopPriceFinder.get_price(book_in_store.get_full_url(),
                                                           book_in_store.book_store.price_css_selector,
                                                           book_in_store.book_store.price_format)

            new_prices.append(BookPrice(0,
                                        book_in_store.book,
                                        book_in_store.book_store,
                                        new_price_value,
                                        datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")))
        except Exception as ex:
            logging.error(f"Failed get updated price from {full_url}")
            logging.error(f"Exception: {ex}")

    return new_prices


def get_updated_prices_for_books(book_stores_queue, updated_book_prices):
    while not book_stores_queue.empty():
        book_stores_for_book = book_stores_queue.get()
        new_prices_for_book = get_updated_prices_for_book(book_stores_for_book)
        updated_book_prices.extend(new_prices_for_book)


def run():
    args = parse_arguments()
    configuration = ConfigLoader.load(args.configuration)
    setup_logging(configuration.logfile, configuration.loglevel)

    logging.info("Config loaded!")
    logging.info("Reading books from DB...")
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    books = books_db.get_books()
    logging.debug(f"{len(books)} books read.")

    logging.info("Reading book stores for books...")
    book_store_data_by_book_id = books_db.get_book_stores_for_books(books)
    books_with_store_count = len(book_store_data_by_book_id)
    logging.debug(f"Book stores found for {books_with_store_count} books.")

    book_store_queue = create_book_store_queue(book_store_data_by_book_id)
    thread_count = MAX_THREAD_COUNT if books_with_store_count >= MAX_THREAD_COUNT else books_with_store_count
    logging.info(f"Updating prices for books using {thread_count} threads...")
    threads = []
    updated_book_prices = []
    for _ in range(thread_count):
        t = Thread(target=get_updated_prices_for_books, args=(book_store_queue, updated_book_prices, ))
        threads.append(t)
        t.start()

    [t.join() for t in threads]

    logging.info(f"Inserting {len(updated_book_prices)} prices to DB....")
    books_db.create_prices(updated_book_prices)
    logging.info(f"Prices inserted!")


if __name__ == "__main__":
    run()
