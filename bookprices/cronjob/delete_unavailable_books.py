#!/usr/bin/env python3
import os
import logging
import sys
import shared
from bookprices.shared.config import loader
from bookprices.shared.db.database import Database
from bookprices.shared.model.error import FailedUpdateReason


LOG_FILE_NAME = f"{os.path.basename(__file__)}.log"


class DeleteUnavailableBooksJob:
    FAILED_UPDATE_LIMIT = 3

    def __init__(self, db: Database):
        self.db = db

    def run(self):
        logging.info("Deleting unavailable books...")
        books = self.db.book_db.get_books()
        bookstores_for_books = self.db.bookstore_db.get_bookstores_for_books(books)
        delete_count = 0
        for book_id, bookstores in bookstores_for_books.items():
            for bookstore_book in bookstores:
                if self.is_book_unavailable(book_id, bookstore_book.book_store.id):
                    delete_count += 1
                    logging.info(f"Deleting book {book_id} from bookstore {bookstore_book.book_store.id}")
                    self.db.bookstore_db.delete_book_from_bookstore(book_id, bookstore_book.book_store.id)
        logging.info(f"Deleted {delete_count} unavailable books from bookstores!")

    def is_book_unavailable(self, book_id: int, bookstore_id: int):
        failed_price_updates = self.db.bookprice_db.get_failed_price_updates(
            book_id, bookstore_id, self.FAILED_UPDATE_LIMIT)
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
