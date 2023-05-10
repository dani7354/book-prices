class Database:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name


class Config:
    def __init__(self, database, logdir, imgdir, loglevel):
        self.database = database
        self.logdir = logdir
        self.imgdir = imgdir
        self.loglevel = loglevel



