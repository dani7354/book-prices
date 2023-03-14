import json


class Database:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name


class Config:
    def __init__(self, database, logdir, loglevel):
        self.database = database
        self.logdir = logdir
        self.loglevel = loglevel


class ConfigLoader:
    @staticmethod
    def _load_from_json(file) -> dict:
        with open(file, "r") as json_file:
            return json.load(json_file)

    @classmethod
    def load(cls, file) -> Config:
        json_content = cls._load_from_json(file)
        database_section = json_content["database"]

        return Config(Database(database_section["host"],
                               database_section["port"],
                               database_section["username"],
                               database_section["password"],
                               database_section["name"]),
                      json_content["logdir"],
                      json_content["loglevel"])

