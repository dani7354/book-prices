#!/usr/bin/env python3
import argparse
import requests
from threading import Thread
from bookprices.shared.db.database import Database
from bookprices.shared.config import loader
from bookprices.shared.model.book import Book
from queue import Queue


class CacheFiller:
    def __init__(self, db: Database, base_url: str, threads: int):
        self._db = db
        self._base_url = base_url
        self._threads = threads
        self._book_queue = Queue()

    def run(self) -> None:
        self._fill_book_queue(self._db)
        self._start_threads()

    def _start_threads(self) -> None:
        threads = []
        for _ in range(self._threads):
            t = Thread(target=self._cache_pages_for_next_book)
            threads.append(t)
            t.start()
        [t.join() for t in threads]

    def _cache_pages_for_next_book(self) -> None:
        while not self._book_queue.empty():
            book = self._book_queue.get()
            urls = self._get_urls_for_book(self._db, book, self._base_url)
            print(f"{len(urls)} created for book {book.id}")
            for url in urls:
                response = requests.get(url, verify=False)
                print(f"{url} => {response.status_code}...")

    def _fill_book_queue(self, database: Database) -> None:
        books = database.book_db.get_books()
        print(f"{len(books)} books will be cached!")
        for book in books:
            self._book_queue.put(book)

    @staticmethod
    def _get_urls_for_book(database: Database, book: Book, base_url: str) -> list[str]:
        book_details_page_url = f"{base_url}/book/{book.id}"
        book_details_data_url = f"{base_url}/api/book/{book.id}"
        urls = [book_details_page_url, book_details_data_url]

        book_stores_for_book = database.bookstore_db.get_bookstores_for_books([book])
        for _, stores in book_stores_for_book.items():
            for store in stores:
                urls.append(f"{base_url}/book/{book.id}/store/{store.book_store.id}")
                urls.append(f"{base_url}/api/book/{book.id}/store/{store.book_store.id}")

        return urls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)
    parser.add_argument("-b", "--base-url", dest="base_url", type=str, required=True)
    parser.add_argument("-t", "--threads", dest="threads", type=int, default=12)
    return parser.parse_args()


def main():
    args = parse_args()
    configuration = loader.load(args.configuration)
    database = Database(configuration.database.db_host,
                        configuration.database.db_port,
                        configuration.database.db_user,
                        configuration.database.db_password,
                        configuration.database.db_name)

    filler = CacheFiller(database, args.base_url, args.threads)
    filler.run()


if __name__ == "__main__":
    main()
