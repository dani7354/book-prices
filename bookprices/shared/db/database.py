from bookprices.shared.db.api import ApiKeyDb
from bookprices.shared.db.book import BookDb
from bookprices.shared.db.bookstore import BookStoreDb
from bookprices.shared.db.bookprice import BookPriceDb
from bookprices.shared.db.status import StatusDb
from bookprices.shared.db.user import UserDb


class Database:
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_name: str):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name

        self.book_db = BookDb(
            self.db_host,
            self.db_port,
            self.db_user,
            self.db_password,
            self.db_name)

        self.bookstore_db = BookStoreDb(
            self.db_host,
            self.db_port,
            self.db_user,
            self.db_password,
            self.db_name)

        self.bookprice_db = BookPriceDb(
            self.db_host,
            self.db_port,
            self.db_user,
            self.db_password,
            self.db_name)

        self.user_db = UserDb(
            self.db_host,
            self.db_port,
            self.db_user,
            self.db_password,
            self.db_name)

        self.status_db = StatusDb(
                self.db_host,
                self.db_port,
                self.db_user,
                self.db_password,
                self.db_name)

        self.api_key_db = ApiKeyDb(
            self.db_host,
            self.db_port,
            self.db_user,
            self.db_password,
            self.db_name)
