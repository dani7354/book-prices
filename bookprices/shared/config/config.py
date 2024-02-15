from dataclasses import dataclass


@dataclass(frozen=True)
class Database:
    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str


@dataclass(frozen=True)
class Config:
    database: Database
    logdir: str
    imgdir: str
    loglevel: int
