from dataclasses import dataclass


@dataclass(frozen=True)
class Database:
    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str


@dataclass(frozen=True)
class Cache:
    host: str
    port: int
    database: int


@dataclass(frozen=True)
class JobApi:
    base_url: str
    api_username: str
    api_password: str


@dataclass(frozen=True)
class Config:
    database: Database
    cache: Cache
    job_api: JobApi
    logdir: str
    imgdir: str
    loglevel: str
