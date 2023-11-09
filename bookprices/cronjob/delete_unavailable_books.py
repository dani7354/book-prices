#!/usr/bin/env python3
import os
import logging
import sys
import shared
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.model.error import FailedUpdateReason, FailedPriceUpdateCount


LOG_FILE_NAME = "delete_unavailable_books.log"


class DeleteUnavailableBooksJob:
    FAILED_UPDATE_LIMIT = 3

    def __init__(self, db: Database):
        self.db = db

    def run(self):
        logging.info("Deleting unavailable books...")
        failed_price_update_counts = self.db.bookprice_db.get_failed_price_update_counts()
        delete_count = 0
        for failed_update_count in failed_price_update_counts:
            if self._is_book_unavailable(failed_update_count):
                delete_count += 1
                logging.info("Deleting book %s from bookstore %s",
                             failed_update_count.book_id, failed_update_count.bookstore_id)
                self.db.bookstore_db.delete_book_from_bookstore(
                    failed_update_count.book_id, failed_update_count.bookstore_id)
                logging.info("Deleting failed price updates for book %s from bookstore %s",
                             failed_update_count.book_id, failed_update_count.bookstore_id)
                self.db.bookprice_db.delete_failed_price_updates(
                    failed_update_count.book_id, failed_update_count.bookstore_id)

        logging.info(f"Deleted {delete_count} unavailable books from bookstores!")

    def _is_book_unavailable(self, failed_update_count: FailedPriceUpdateCount):
        if failed_update_count.count < self.FAILED_UPDATE_LIMIT:
            return False

        failed_price_updates = self.db.bookprice_db.get_latest_failed_price_updates(
            failed_update_count.book_id, failed_update_count.bookstore_id, self.FAILED_UPDATE_LIMIT)
        if len(failed_price_updates) < self.FAILED_UPDATE_LIMIT:
            return False

        return all(f.reason == FailedUpdateReason.PAGE_NOT_FOUND for f in failed_price_updates)


def main():
    try:
        args = shared.parse_arguments()
        configuration = loader.load(args.configuration)
        shared.setup_logging(configuration.logdir, LOG_FILE_NAME, configuration.loglevel)
        logging.info("Config loaded!")

        db = Database(configuration.database.db_host,
                      configuration.database.db_port,
                      configuration.database.db_user,
                      configuration.database.db_password,
                      configuration.database.db_name)

        delete_unavailable_books_job = DeleteUnavailableBooksJob(db)
        delete_unavailable_books_job.run()
    except Exception as ex:
        logging.fatal("An error occurred while deleting unavailable books!")
        logging.fatal(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
