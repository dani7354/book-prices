#!/usr/bin/env python3
import logging
import sys
from datetime import date, timedelta
from bookprices.cronjob import shared
from bookprices.shared.db.database import Database
from bookprices.shared.db.bookprice import BookPriceDb
from bookprices.shared.config import loader


LOG_FILE_NAME = "delete_prices.log"


class DeletePricesJob:
    PRICE_MAX_AGE_DAYS = 90

    def __init__(self, bookprice_db: BookPriceDb):
        self.bookprice_db = bookprice_db

    def run(self):
        earliest_date = date.today() - timedelta(days=self.PRICE_MAX_AGE_DAYS)
        logging.info(f"Deleting prices older than {str(earliest_date)}")

        self.bookprice_db.delete_prices_older_than(earliest_date)
        logging.info("Prices deleted!")


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

        delete_prices_job = DeletePricesJob(books_db.bookprice_db)
        delete_prices_job.run()
    except Exception as ex:
        logging.error("An error occurred while deleting prices!")
        logging.error(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
