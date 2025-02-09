import json
from bookprices.shared.config.config import Config, Database, Cache, JobApi


def _load_from_json(file) -> dict:
    with open(file, "r") as json_file:
        return json.load(json_file)


def load(file) -> Config:
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
