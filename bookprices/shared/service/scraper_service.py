import logging

from bookprices.shared.webscraping.bookstore import BookStoreScraper


class BookStoreScraperService:
    """ Service for listing and getting bookstore scrapers """
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._scrapers = {}

    def add_scraper(self, scraper: BookStoreScraper) -> None:
        self._scrapers[scraper.name] = scraper

    def list_scrapers(self) -> list[BookStoreScraper]:
        pass

    def get_scraper(self, scraper_id: str) -> BookStoreScraper | None:
        pass

