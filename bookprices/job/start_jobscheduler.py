from bookprices.job.scheduler.jobscheduler import JobScheduler
from bookprices.shared.api.job import JobApiClient
from bookprices.shared.config import loader
from bookprices.shared.db.api import ApiKeyDb
from bookprices.shared.log import setup_logging
from bookprices.shared.service.job_service import JobService

JOB_API_CLIENT_ID = "JobApiJobScheduler"
PROGRAM_NAME = "JobScheduler"


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
    job_service = JobService(job_api_client)
    job_scheduler = JobScheduler(job_service, config.scheduler.jobs)



if __name__ == "__main__":
    main()
