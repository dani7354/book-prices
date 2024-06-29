#!/usr/bin/env python3
import logging
import sys
from datetime import date, timedelta
from bookprices.cronjob import shared
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.db.database import Database
from bookprices.shared.db.bookprice import BookPriceDb
from bookprices.shared.config import loader


LOG_FILE_NAME = "delete_prices.log"


class DeletePricesJob:
    PRICE_MAX_AGE_DAYS = 365

    def __init__(self, bookprice_db: BookPriceDb, cache_key_remover: BookPriceKeyRemover):
        self.bookprice_db = bookprice_db
        self._cache_key_remover = cache_key_remover

    def run(self):
        earliest_date = date.today() - timedelta(days=self.PRICE_MAX_AGE_DAYS)
        logging.info(f"Deleting prices older than {str(earliest_date)}")

        bookprice_ids = self.bookprice_db.get_prices_older_than(earliest_date)
        logging.info(f"Found {len(bookprice_ids)} prices to delete")

        ids_to_delete = [bookprice_id.id for bookprice_id in bookprice_ids]
        if not ids_to_delete:
            logging.info("No prices to delete!")
            return

        logging.info("Deleting prices from the database...")
        self.bookprice_db.delete_prices(ids_to_delete)

        logging.info("Removing cache keys for affected books and bookstores...")
        for ids in bookprice_ids:
            self._cache_key_remover.remove_keys_for_book(ids.book_id)
            self._cache_key_remover.remove_keys_for_book_and_bookstore(ids.book_id, ids.bookstore_id)

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

        cache_key_remover = BookPriceKeyRemover(
            RedisClient(configuration.cache.host, configuration.cache.database, configuration.cache.port))

        delete_prices_job = DeletePricesJob(books_db.bookprice_db, cache_key_remover)
        delete_prices_job.run()
    except Exception as ex:
        logging.error("An error occurred while deleting prices!")
        logging.error(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
