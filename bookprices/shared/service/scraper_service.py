import logging

from bookprices.shared.db.tables import BookStore
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.webscraping.bookstore import (
    BookStoreScraper, StaticBookStoreScraper, BookStoreConfiguration, WilliamDamScraper, SaxoScraper, BogOgIdeScraper,
    PlusbogScraper, ThiemersScraper, GuccaScraper)


class BookStoreScraperService:
    """ Service for listing and getting bookstore scrapers """

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._unit_of_work = unit_of_work
        self._scraper_types = {
            StaticBookStoreScraper.get_name(): StaticBookStoreScraper,
            WilliamDamScraper.get_name(): WilliamDamScraper,
            SaxoScraper.get_name(): SaxoScraper,
            BogOgIdeScraper.get_name(): BogOgIdeScraper,
            # PlusbogScraper.get_name(): PlusbogScraper,
            ThiemersScraper.get_name(): ThiemersScraper,
            GuccaScraper.get_name(): GuccaScraper,
        }

    def list_scrapers(self) -> list[BookStoreScraper]:
        with self._unit_of_work as uow:
            bookstores = uow.bookstore_repository.get_list()

        return [scraper for bookstore in bookstores if (scraper := self._create_scraper_for_bookstore(bookstore))]

    def get_scraper(self, bookstore_id: int) -> BookStoreScraper | None:
        with self._unit_of_work as uow:
            if not (bookstore := uow.bookstore_repository.get(bookstore_id)):
                self._logger.warning(f"Bookstore with id {bookstore_id} not found.")
                return None

        return self._create_scraper_for_bookstore(bookstore)

    def get_scraper_names(self) -> list[str]:
        return list(self._scraper_types.keys())

    def _create_scraper_for_bookstore(self, bookstore: BookStore) -> BookStoreScraper | None:
        if not (scraper_class := self._scraper_types.get(bookstore.scraper_id)):
            self._logger.warning(f"No scraper found for bookstore {bookstore.name}")
            return None

        configuration = BookStoreConfiguration(
            bookstore_id=bookstore.id,
            bookstore_name=bookstore.name,
            bookstore_url=bookstore.url,
            bookstore_search_url=bookstore.search_url,
            bookstore_price_css_selector=bookstore.price_css_selector,
            bookstore_price_format=bookstore.price_format,
            bookstore_isbn_css_selector=bookstore.isbn_css_selector,
            search_result_css_selector=bookstore.search_result_css_selector)

        return scraper_class(configuration)
