#!/usr/bin/env python3
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configuration.config import ConfigLoader
from book_source.web import SitemapBookFinder
from data.bookprice_db import BookPriceDb

MAX_THREAD_COUNT = 10


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", dest="words", type=str, nargs="*", required=True)
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def search_sitemaps(sitemaps: list, words: list) -> list:
    sitemap_finder = SitemapBookFinder(max_thread_count=MAX_THREAD_COUNT)
    all_matched_urls = []
    for sitemap in sitemaps:
        print(f"Reading sitemap {sitemap.url} for book store {sitemap.book_store.name} (id {sitemap.book_store.id})...")
        matched_urls = sitemap_finder.search_sitemap(sitemap.url, words)
        print(f"Found {len(matched_urls)} matches!")
        all_matched_urls.extend(matched_urls)

    return all_matched_urls


def run():
    args = parse_arguments()
    configuration = ConfigLoader.load(args.configuration)
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    sitemaps = books_db.get_sitemaps()
    matches = search_sitemaps(sitemaps, args.words)

    for m in matches:
        print(m)

if __name__ == "__main__":
    run()
