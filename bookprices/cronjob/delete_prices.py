#!/usr/bin/env python3
import shared
import logging
from datetime import date, timedelta

from bookprices.shared.db.bookprice import BookPriceDb
from bookprices.shared.config import loader


PRICE_MAX_AGE_DAYS = 30
LOG_FILE_NAME = "delete_prices.log"


def run():
    args = shared.parse_arguments()
    configuration = loader.load(args.configuration)
    shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)

    logging.info("Config loaded!")
    logging.info("Deleting books from DB...")
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    earliest_date = date.today() - timedelta(days=PRICE_MAX_AGE_DAYS)
    logging.info(f"Deleting prices older than {str(earliest_date)}")
    books_db.delete_prices_older_than(earliest_date)
    logging.info("Prices deleted!")


if __name__ == "__main__":
    run()

