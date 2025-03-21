from bookprices.job.job.trim_prices import TrimPricesJob
from bookprices.job.runner.jobrunner import JobRunner
from bookprices.job.runner.service import RunnerJobService
from bookprices.shared.api.job import JobApiClient
from bookprices.shared.cache.client import RedisClient
from bookprices.shared.cache.key_remover import BookPriceKeyRemover
from bookprices.shared.config import loader
from bookprices.shared.config.config import Config
from bookprices.shared.db.api import ApiKeyDb
from bookprices.shared.db.database import Database
from bookprices.shared.log import setup_logging

JOB_API_CLIENT_ID = "JobApiJobRunner"
PROGRAM_NAME = "JobRunner"


def create_trim_prices_job(config: Config) -> TrimPricesJob:
    cache_key_remover = BookPriceKeyRemover(
        RedisClient(
            config.cache.host,
            config.cache.database,
            config.cache.port))
    db = Database(
        config.database.db_host,
        config.database.db_port,
        config.database.db_user,
        config.database.db_password,
        config.database.db_name)

    return TrimPricesJob(config, cache_key_remover, db)


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
    jobs = [create_trim_prices_job(config)]
    job_runner = JobRunner(config, jobs, service)
    job_runner.start()


if __name__ == "__main__":
    main()