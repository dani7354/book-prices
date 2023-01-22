#!/usr/bin/env python3
import argparse
from configuration.config import ConfigLoader
from price_source.web import SitemapBookFinder
from data.bookprice_db import BookPriceDb

MAX_THREAD_COUNT = 10


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", dest="words", type=str, nargs="*", required=True)
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def run():
    args = parse_arguments()
    configuration = ConfigLoader.load(args.configuration)
    books_db = BookPriceDb(configuration.database.db_host,
                           configuration.database.db_port,
                           configuration.database.db_user,
                           configuration.database.db_password,
                           configuration.database.db_name)

    sitemap_finder = SitemapBookFinder(max_thread_count=MAX_THREAD_COUNT)
    all_matched_urls = []
    for sitemap in books_db.get_sitemaps():
        print(f"Reading sitemap {sitemap.url} for book store {sitemap.book_store.name}...")
        matched_urls = sitemap_finder.search_sitemap(sitemap.url, args.words)
        print(f"Found {len(matched_urls)} matches!")
        all_matched_urls.extend(matched_urls)

    for m in all_matched_urls:
        print(m)


if __name__ == "__main__":
    run()
