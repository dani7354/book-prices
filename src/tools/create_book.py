#!/usr/bin/env python3
import argparse
import os
import sys
from urllib.parse import urlparse
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configuration.config import ConfigLoader
from book_source.web import SitemapBookFinder, WebsiteBookFinder
from data.bookprice_db import BookPriceDb
from data.model import Book

MAX_THREAD_COUNT = 10


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title", dest="title", type=str, required=True)
    parser.add_argument("-a", "--author", dest="author", type=str, required=True)
    parser.add_argument("-i", "--isbn", dest="isbn", type=str, required=True)
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def search_sitemaps(sitemaps: list, isbn: str) -> list:
    sitemap_finder = SitemapBookFinder(max_thread_count=MAX_THREAD_COUNT)
    matches = []
    for sitemap in sitemaps:
        print(f"Reading sitemap {sitemap.url} for book store {sitemap.book_store.name} (id {sitemap.book_store.id})...")
        matched_urls = sitemap_finder.search_sitemap(sitemap.url, [isbn])

        if len(matched_urls) > 0:
            matches.append((sitemap.book_store.id, urlparse(matched_urls[0]).path))

    return matches


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
    configuration = ConfigLoader.load(args.configuration)
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    all_matches = []

    print("Getting sitemaps...")
    sitemaps = books_db.get_sitemaps()
    print(f"Found {len(sitemaps)} sitemaps!")

    print(f"Searching sitemaps for ISBN {args.isbn}...")
    matches_from_sitemaps = search_sitemaps(sitemaps, args.isbn)
    print(f"{len(matches_from_sitemaps)} URLs found!")
    all_matches.extend(matches_from_sitemaps)

    book_stores_website_search = []
    for book_store in books_db.get_book_stores():
        if book_store.search_url is not None:
            book_stores_website_search.append(book_store)

    print(f"Searching websites for ISBN {args.isbn}...")
    matches_from_websites = search_website(book_stores_website_search, args.isbn)
    print(f"{len(matches_from_websites)} URLs found!")
    all_matches.extend(matches_from_websites)

    print(f"Creating new book: {args.title} by {args.author}...")
    new_book = Book(0, args.title, args.author, None)
    new_book_id = books_db.create_book(new_book)
    if new_book_id == -1:
        print("Failed to add book!")
        exit(1)

    print(f"New book created with id {new_book_id}")

    print(f"Inserting {len(all_matches)} URLs...")
    for store_id, url in all_matches:
        try:
            books_db.create_book_store_for_book(new_book_id, store_id, url)
        except Exception as ex:
            print(f"Error while inserting url {url} for book {new_book_id} and book store {store_id}.")
            continue

    print("Book and urls added!")


if __name__ == "__main__":
    run()
