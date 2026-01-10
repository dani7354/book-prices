import logging

from bookprices.job.job.base import DEFAULT_THREAD_COUNT
from bookprices.job.job.bookstore_search import BookStoreSearchJob
from bookprices.job.job.delete_images import DeleteImagesJob
from bookprices.job.job.delete_prices import DeletePricesJob
from bookprices.job.job.delete_unavailable_books import DeleteUnavailableBooksJob
from bookprices.job.job.download_images import DownloadImagesJob, DownloadImagesForBooksJob
from bookprices.job.job.import_books import WilliamDamBookImportJob
from bookprices.job.job.trim_prices import TrimPricesJob
from bookprices.job.job.update_prices import AllBookPricesUpdateJob, BookPricesUpdateJob
from bookprices.job.job.update_prices_new import AllBookPricesUpdateJobNew
from bookprices.job.runner.jobrunner import JobRunner
from bookprices.job.runner.service import RunnerJobService
from bookprices.job.service.image_download import ImageDownloadService
from bookprices.job.service.price_update import PriceUpdateService, NewPriceUpdateService
from bookprices.shared.api.job import JobApiClient
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config import loader
from bookprices.shared.config.config import Config
from bookprices.shared.db.api import ApiKeyDb
from bookprices.shared.db.database import Database
from bookprices.shared.event.base import EventManager, Event
from bookprices.shared.event.enum import BookPricesEvents
from bookprices.shared.event.listener import StartJobListener
from bookprices.shared.log import setup_logging
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.job_service import JobService
from bookprices.shared.service.scraper_service import BookStoreScraperService
from bookprices.shared.webscraping.image import ImageDownloader
from bookprices.shared.service.book_image_file_service import BookImageFileService
from bookprices.web.shared.db_session import SessionFactory

THREAD_COUNT = 8
JOB_API_CLIENT_ID = "JobApiJobRunner"
PROGRAM_NAME = "JobRunner"


def create_database_container(config: Config) -> Database:
    return Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)


def create_cache_key_remover(config: Config) -> BookPriceKeyRemover:
    return BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))


def create_job_api_client(config: Config) -> JobApiClient:
    api_key_db = ApiKeyDb(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    api_client = JobApiClient(
        config.job_api.base_url,
        config.job_api.api_username,
        config.job_api.api_password,
        JOB_API_CLIENT_ID,
        api_key_db)

    return api_client


def create_job_service(config: Config) -> JobService:
    job_api_client = create_job_api_client(config)
    return JobService(job_api_client)


def create_runner_job_service(config: Config) -> RunnerJobService:
    api_client = create_job_api_client(config)
    return RunnerJobService(api_client)


def setup_event_manager(config: Config) -> EventManager:
    job_service = create_job_service(config)

    prices_updated_event = Event(str(BookPricesEvents.BOOK_PRICES_UPDATED))
    prices_updated_event.add_listener(StartJobListener(job_service, TrimPricesJob.name))

    book_created_event = Event(str(BookPricesEvents.BOOK_CREATED))

    books_imported_event = Event(str(BookPricesEvents.BOOKS_IMPORTED))
    books_imported_event.add_listener(StartJobListener(job_service, DownloadImagesJob.name))
    book_created_event.add_listener(StartJobListener(job_service, BookStoreSearchJob.name))

    book_deleted_event = Event(str(BookPricesEvents.BOOKS_DELETED))
    book_deleted_event.add_listener(StartJobListener(job_service, DeleteImagesJob.name))

    books_found_in_stores = Event(str(BookPricesEvents.BOOKSTORE_SEARCH_COMPLETED))
    books_found_in_stores.add_listener(StartJobListener(job_service, DownloadImagesJob.name))

    events = {
        prices_updated_event.name: prices_updated_event,
        book_created_event.name: book_created_event,
        book_deleted_event.name: book_deleted_event,
        books_found_in_stores.name: books_found_in_stores,
        books_imported_event.name: books_imported_event
    }
    event_manager = EventManager(events)

    return event_manager


def create_trim_prices_job(config: Config) -> TrimPricesJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)

    return TrimPricesJob(config, cache_key_remover, db)


def create_download_images_job(config: Config) -> DownloadImagesJob:
    db = create_database_container(config)
    book_image_file_service = BookImageFileService(config.imgdir)
    image_downloader = ImageDownloader(book_image_file_service, config.imgdir)
    thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT
    image_download_service = ImageDownloadService(db, image_downloader, thread_count)

    return DownloadImagesJob(config, db, image_download_service)


def create_download_images_for_books_job(config: Config) -> DownloadImagesForBooksJob:
    db = create_database_container(config)
    book_image_file_service = BookImageFileService(config.imgdir)
    image_downloader = ImageDownloader(book_image_file_service, config.imgdir)
    thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT
    image_download_service = ImageDownloadService(db, image_downloader, thread_count)

    return DownloadImagesForBooksJob(config, db, image_download_service)


def create_delete_unavailable_books_job(config: Config, event_manager: EventManager) -> DeleteUnavailableBooksJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)

    return DeleteUnavailableBooksJob(config, db, cache_key_remover, event_manager)


def create_delete_images_job(config: Config) -> DeleteImagesJob:
    db = create_database_container(config)
    book_image_file_service = BookImageFileService(config.imgdir)

    return DeleteImagesJob(config, db, book_image_file_service)


def create_bookstore_search_job(config: Config, event_manager: EventManager) -> BookStoreSearchJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)

    return BookStoreSearchJob(config, db, cache_key_remover, event_manager)


def create_delete_prices_job(config: Config) -> DeletePricesJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)

    return DeletePricesJob(config, db, cache_key_remover)


def create_all_book_prices_update_job(config: Config, event_manager: EventManager) -> AllBookPricesUpdateJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)
    thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT
    price_update_service = PriceUpdateService(db, cache_key_remover, thread_count)

    return AllBookPricesUpdateJob(config, db, price_update_service, event_manager)


def create_all_book_prices_update_job_new(config: Config, event_manager: EventManager) -> AllBookPricesUpdateJobNew:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)
    session_factory = SessionFactory()
    unit_of_work = UnitOfWork(session_factory)
    scraper_service = BookStoreScraperService(unit_of_work)
    thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT
    price_update_service = NewPriceUpdateService(db, cache_key_remover, unit_of_work, scraper_service, thread_count)

    return AllBookPricesUpdateJobNew(config, unit_of_work, price_update_service, event_manager)


def create_book_price_update_job(config: Config, event_manager: EventManager) -> BookPricesUpdateJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)
    thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT
    price_update_service = PriceUpdateService(db, cache_key_remover,  thread_count)

    return BookPricesUpdateJob(config, price_update_service, event_manager)


def create_william_dam_book_import_job(config: Config, event_manager: EventManager) -> WilliamDamBookImportJob:
    db = create_database_container(config)
    cache_key_remover = create_cache_key_remover(config)

    return WilliamDamBookImportJob(config, db, cache_key_remover, event_manager)


def main() -> None:
    config = loader.load_from_env()
    setup_logging(config, PROGRAM_NAME)
    logging.info("Config loaded successfully. Logging setup.")

    logging.info("Setting up required services and job instances...")
    event_manager = setup_event_manager(config)
    job_api_client = create_job_api_client(config)
    service = RunnerJobService(job_api_client)
    jobs = [
        create_trim_prices_job(config),
        create_download_images_job(config),
        create_delete_unavailable_books_job(config, event_manager),
        create_delete_images_job(config),
        create_bookstore_search_job(config, event_manager),
        create_delete_prices_job(config),
        create_book_price_update_job(config, event_manager),
        create_all_book_prices_update_job_new(config, event_manager),
        create_all_book_prices_update_job(config, event_manager),
        create_william_dam_book_import_job(config, event_manager)
    ]
    job_runner = JobRunner(config, jobs, service)
    job_runner.start()


if __name__ == "__main__":
    main()
