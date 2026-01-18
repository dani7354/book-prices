from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from bookprices.shared.db.data_session import SessionFactory
from bookprices.web.settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE


class WebSessionFactory(SessionFactory):
    def __init__(self) -> None:
        self.engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")

    def create_session(self) -> Session:
        session_maker = sessionmaker(bind=self.engine)
        return session_maker()

    def create_scoped_session(self) -> Session:
        session_maker = sessionmaker(bind=self.engine)
        return scoped_session(session_maker)()