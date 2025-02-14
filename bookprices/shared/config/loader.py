import json
import os

from bookprices.shared.config.config import Config, Database, Cache, JobApi


def _load_from_json(file) -> dict:
    with open(file, "r") as json_file:
        return json.load(json_file)


def load_from_env() -> Config:
    return Config(
        Database(
            os.environ["MYSQL_SERVER"],
            os.environ["MYSQL_SERVER_PORT"],
            os.environ["MYSQL_USER"],
            os.environ["MYSQL_PASSWORD"],
            os.environ["MYSQL_DATABASE"]),
                  Cache(
                      os.environ["REDIS_SERVER"],
                      int(os.environ["REDIS_SERVER_PORT"]),
                      int(os.environ["CACHE_REDIS_DB"])),
                  JobApi(
                      os.environ["JOB_API_BASE_URL"],
                      os.environ["JOB_API_USERNAME"],
                      os.environ["JOB_API_PASSWORD"]),
                  os.environ["LOG_DIR"],
                  os.environ["IMAGE_DIR"],
                  os.environ["LOG_LEVEL"])


def load_from_file(file: str) -> Config:
    json_content = _load_from_json(file)
    database_section = json_content["database"]
    cache_section = json_content["cache"]
    job_api_section = json_content["job_api"]

    return Config(Database(database_section["host"],
                           database_section["port"],
                           database_section["username"],
                           database_section["password"],
                           database_section["name"]),
                  Cache(cache_section["host"],
                        int(cache_section["port"]),
                        int(cache_section["database"])),
                  JobApi(job_api_section["api_base_url"],
                         job_api_section["api_username"],
                         job_api_section["api_password"]),
                  json_content["logdir"],
                  json_content["imgdir"],
                  json_content["loglevel"])
