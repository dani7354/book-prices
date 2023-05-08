import requests
from threading import Thread
from queue import Queue
from xml.etree import ElementTree


LOC_ELEMENT = "loc"
SITEMAP_ELEMENT = "sitemap"
URL_ELEMENT = "url"


class SitemapBookFinder:

    def __init__(self, max_thread_count: int):
        self.max_thread_count = max_thread_count
        self.ns = {"": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def search_sitemap(self, url: str, words: list) -> list:
        matched_book_urls = []
        sitemap_urls = self._get_site_map_page_urls(url)
        sitemap_url_queue = self._create_sitemap_urls_queue(sitemap_urls)
        thread_count = self.max_thread_count if len(sitemap_urls) >= self.max_thread_count else len(sitemap_urls)

        threads = []
        for _ in range(thread_count):
            t = Thread(target=self._search_sitemaps_for_matches, args=(sitemap_url_queue, words, matched_book_urls,))
            threads.append(t)
            t.start()

        [t.join() for t in threads]

        return matched_book_urls

    def _get_site_map_page_urls(self, url: str):
        response = requests.get(url)
        if response.status_code != 200:
            return []

        xml_tree = ElementTree.fromstring(response.content.decode())
        urls = [sitemap_element.find(LOC_ELEMENT, self.ns).text for sitemap_element in
                xml_tree.findall(SITEMAP_ELEMENT, self.ns)]

        return urls

    def _search_sitemaps_for_matches(self, sitemap_queue: Queue, words: list, matches: list):
        while not sitemap_queue.empty():
            next_sitemap_url = sitemap_queue.get()
            matches_from_sitemap = self._search_for_matches_in_sitemap(next_sitemap_url, words)
            matches.extend(matches_from_sitemap)

    def _search_for_matches_in_sitemap(self, url: str, words: list) -> list:
        matched_book_urls = []
        sitemap_response = requests.get(url)
        if sitemap_response.status_code != 200:
            return matched_book_urls

        sitemap_xml_tree = ElementTree.fromstring(sitemap_response.content.decode())
        for book_url in sitemap_xml_tree.findall(URL_ELEMENT, self.ns):
            book_url_text = book_url.find(LOC_ELEMENT, self.ns).text
            for word in words:
                if word in book_url_text:
                    print(f"Match for '{word}': {book_url_text}")
                    matched_book_urls.append(book_url_text)

        return matched_book_urls

    @staticmethod
    def _create_sitemap_urls_queue(sitemap_urls) -> Queue:
        sitemap_urls_queue = Queue()
        for url in sitemap_urls:
            sitemap_urls_queue.put(url)

        return sitemap_urls_queue
