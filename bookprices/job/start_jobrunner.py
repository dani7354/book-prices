from bookprices.job.job.bookstore_search import BookStoreSearchJob
from bookprices.job.job.delete_images import DeleteImagesJob
from bookprices.job.job.delete_prices import DeletePricesJob
from bookprices.job.job.delete_unavailable_books import DeleteUnavailableBooksJob
from bookprices.job.job.download_images import DownloadImagesJob
from bookprices.job.job.trim_prices import TrimPricesJob
from bookprices.job.job.update_prices import AllPricesUpdateJob
from bookprices.job.runner.jobrunner import JobRunner
from bookprices.job.runner.service import RunnerJobService
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
from bookprices.shared.webscraping.image import ImageDownloader

JOB_API_CLIENT_ID = "JobApiJobRunner"
PROGRAM_NAME = "JobRunner"


def create_api_client(config: Config) -> JobApiClient:
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


def create_job_service(config: Config) -> RunnerJobService:
    api_client = create_api_client(config)
    return RunnerJobService(api_client)


def get_event_manager(config: Config) -> EventManager:
    job_service = create_job_service(config)

    prices_updated_event = Event(BookPricesEvents.BOOK_PRICE_UPDATED.value)
    prices_updated_event.add_listener(StartJobListener(job_service, TrimPricesJob.name))

    book_created_event = Event(BookPricesEvents.BOOK_CREATED.value)
    book_created_event.add_listener(StartJobListener(job_service, DownloadImagesJob.name))
    book_created_event.add_listener(StartJobListener(job_service, BookStoreSearchJob.name))

    events = {
        prices_updated_event.name: prices_updated_event,
        book_created_event.name: book_created_event
    }
    event_manager = EventManager(events)

    return event_manager


def create_trim_prices_job(config: Config) -> TrimPricesJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))

    return TrimPricesJob(config, cache_key_remover, db)


def create_download_images_job(config: Config) -> DownloadImagesJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    image_downloader = ImageDownloader(config.imgdir)

    return DownloadImagesJob(config, db, image_downloader)

def create_delete_unavailable_books_job(config: Config) -> DeleteUnavailableBooksJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))

    return DeleteUnavailableBooksJob(config, db, cache_key_remover)


def create_delete_images_job(config: Config) -> DeleteImagesJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    return DeleteImagesJob(config, db)


def create_bookstore_search_job(config: Config) -> BookStoreSearchJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))

    return BookStoreSearchJob(config, db, cache_key_remover)


def create_delete_prices_job(config: Config) -> DeletePricesJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))

    return DeletePricesJob(config, db, cache_key_remover)


def create_all_prices_update_job(config: Config) -> AllPricesUpdateJob:
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))

    return AllPricesUpdateJob(config, db, cache_key_remover)


def main() -> None:
    config = loader.load_from_env()
    setup_logging(config, PROGRAM_NAME)
    api_key_db = ApiKeyDb(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    job_api_client = JobApiClient(
        config.job_api.base_url,
        config.job_api.api_username,
        config.job_api.api_password,
        JOB_API_CLIENT_ID,
        api_key_db)

    service = RunnerJobService(job_api_client)
    jobs = [
        create_trim_prices_job(config),
        create_download_images_job(config),
        create_delete_unavailable_books_job(config),
        create_delete_images_job(config),
        create_bookstore_search_job(config),
        create_delete_prices_job(config),
        create_all_prices_update_job(config)
    ]
    job_runner = JobRunner(config, jobs, service)
    job_runner.start()


if __name__ == "__main__":
    main()
