from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bookprices.web.settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE


class SessionFactory:
    def __init__(self) -> None:
        self.engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")

    def create_session(self) -> Session:
        session_maker = sessionmaker(bind=self.engine)
        return session_maker()