#!/usr/bin/env python3
import argparse
import os
import sys
import isbn_check
from urllib.parse import urlparse
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configuration.config import ConfigLoader
from book_source.web import SitemapBookFinder, WebsiteBookFinder
from data.bookprice_db import BookPriceDb
from data.model import Book


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title", dest="title", type=str, required=True)
    parser.add_argument("-a", "--author", dest="author", type=str, required=True)
    parser.add_argument("-i", "--isbn", dest="isbn", type=str, required=True)
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def search_website(book_stores: list, isbn: str) -> list:
    matches = []
    for book_store in book_stores:
        print(f"Searching {book_store.name} for {isbn}...")
        match_url = WebsiteBookFinder.search_book_isbn(book_store.search_url,
                                                       isbn,
                                                       book_store.search_result_css_selector)

        if match_url is not None:
            print(f"Found match: {match_url}")
            matches.append((book_store.id, urlparse(match_url).path))

    return matches


def run():
    args = parse_arguments()
    if not isbn_check.check_isbn13(args.isbn):
        print(f"{args.isbn} not valid")
        sys.exit(1)

    configuration = ConfigLoader.load(args.configuration)
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    book = books_db.get_book_by_isbn(args.isbn)
    if book is None:
        print(f"Creating new book: {args.title} by {args.author}...")
        book = Book(0, args.isbn, args.title, args.author, None)
        book_id = books_db.create_book(book)
        if book_id == -1:
            print("Failed to add book!")
            sys.exit(1)

        book.id = book_id
        print(f"New book created with id {book.id}")
    else:
        print(f"Book already exists with id {book.id}!")

    book_stores_website_search = []
    for book_store in books_db.get_missing_book_stores(book.id):
        if book_store.search_url is not None:
            book_stores_website_search.append(book_store)
    if len(book_stores_website_search) == 0:
        print("Book already added for available bookstores.")
        sys.exit(0)

    print(f"Searching websites for ISBN {args.isbn}...")
    matches_from_websites = search_website(book_stores_website_search, args.isbn)
    print(f"{len(matches_from_websites)} search URLs found!")

    print(f"Inserting {len(matches_from_websites)} URLs...")
    for store_id, url in matches_from_websites:
        try:
            books_db.create_book_store_for_book(book.id, store_id, url)
        except Exception as ex:
            print(f"Error while inserting url {url} for book {book.id} and book store {store_id}.")
            print(ex)
            continue

    print("Book and urls added!")


if __name__ == "__main__":
    run()
