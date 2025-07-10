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
                      os.getenv("REDIS_SERVER", "localhost"),
                      int(os.getenv("REDIS_SERVER_PORT", 6379)),
                      int(os.getenv("CACHE_REDIS_DB", 0))),
                  JobApi(
                      os.environ["JOB_API_BASE_URL"],
                      os.environ["JOB_API_USERNAME"],
                      os.environ["JOB_API_PASSWORD"]),
                  os.environ["LOG_DIR"],
                  os.getenv("IMAGE_DIR"),
                  os.getenv("LOG_LEVEL", "INFO"),
                  int(thread_count) if (thread_count := os.getenv("JOB_THREAD_COUNT")) else None)


def load_from_file(file: str) -> Config:
    json_content = _load_from_json(file)
    database_section = json_content["database"]
    cache_section = json_content["cache"]
    job_api_section = json_content.get("job_api", {})  # Just until the jobs are fully migrated...

    return Config(Database(database_section["host"],
                           database_section["port"],
                           database_section["username"],
                           database_section["password"],
                           database_section["name"]),
                  Cache(cache_section["host"],
                        int(cache_section["port"]),
                        int(cache_section["database"])),
                  JobApi(job_api_section.get("api_base_url", ""),
                         job_api_section.get("api_username", ""),
                         job_api_section.get("api_password", "")),
                  json_content["logdir"],
                  json_content["imgdir"],
                  json_content["loglevel"])
