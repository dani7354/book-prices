import os

from bookprices.jobrunner.runner.jobrunner import JobRunner
from bookprices.jobrunner.runner.service import RunnerJobService
from bookprices.shared.api.job import JobApiClient
from bookprices.shared.config import loader
from bookprices.shared.db.api import ApiKeyDb


def main() -> None:
    config_path = os.environ["CONFIG_PATH"]

    config = loader.load(config_path)
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
        api_key_db)
    service = RunnerJobService(job_api_client)
    job_runner = JobRunner(config, service)

    job_runner.start()


if __name__ == "__main__":
    main()