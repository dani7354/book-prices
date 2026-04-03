import logging
import traceback

from bookprices.job.db.session import JobSessionFactory
from bookprices.job.scheduler.jobscheduler import JobScheduler
from bookprices.shared.api.job import JobApiClient
from bookprices.shared.config import loader
from bookprices.shared.log import setup_logging
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.job_service import JobService

JOB_API_CLIENT_ID = "JobApiJobScheduler"
PROGRAM_NAME = "JobScheduler"


logger = logging.getLogger(PROGRAM_NAME)


def main() -> None:
    try:
        config = loader.load_from_env()
        setup_logging(config, PROGRAM_NAME)
        job_api_client = JobApiClient(
            config.job_api.base_url,
            config.job_api.api_username,
            config.job_api.api_password,
            JOB_API_CLIENT_ID,
            UnitOfWork(JobSessionFactory(config)))

        job_service = JobService(job_api_client)
        job_scheduler = JobScheduler(job_service)
        job_scheduler.start()
    except Exception as ex:
        logger.error(ex)
        logger.error(traceback.format_exc())
        raise SystemExit(1) from ex


if __name__ == "__main__":
    main()
