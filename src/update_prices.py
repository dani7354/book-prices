#!/usr/bin/env python3
import argparse
import logging
from datetime import datetime
from config import ConfigLoader
from data.bookprice_db import BookPriceDb
from data.model import BookPrice
from price_source.web import WebSource


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


def get_updated_prices_for_book(book_stores) -> list:
    new_prices = []
    for book_in_store in book_stores:
        full_url = book_in_store.get_full_url()
        try:
            logging.debug(f"Getting price for book ID {book_in_store.book.book_id} at book store ID "
                          f"{book_in_store.book_store.id} (URL {full_url})")

            new_price_value = WebSource.get_price(book_in_store.get_full_url(),
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


def get_updated_book_prices(book_stores_by_book_id) -> list:
    all_new_prices = []
    for book_id, book_stores in book_stores_by_book_id.items():
        logging.debug(f"Updating prices for book ID {book_id}...")
        new_prices_for_book = get_updated_prices_for_book(book_stores)
        logging.debug(f"Got {len(new_prices_for_book)} prices for book ID {book_id}")

        all_new_prices.extend(new_prices_for_book)

    return all_new_prices


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
    logging.debug(f"Book stores read for {len(book_store_data_by_book_id)} books.")

    logging.info("Updating prices for books...")
    updated_prices = get_updated_book_prices(book_store_data_by_book_id)

    logging.info(f"Inserting {len(updated_prices)} prices to DB....")
    books_db.create_prices(updated_prices)
    logging.info(f"Prices inserted!")


if __name__ == "__main__":
    run()
