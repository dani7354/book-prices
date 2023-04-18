from mysql.connector import connection


class BaseDb:
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_name: str):
        self.db_host = db_host
        self.db_port = db_port,
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

    def get_connection(self) -> connection:
        con = connection.MySQLConnection(host=self.db_host,
                                         user=self.db_user,
                                         password=self.db_password,
                                         database=self.db_name)
        return con
