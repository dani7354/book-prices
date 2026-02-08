from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from bookprices.shared.config.config import Config
from bookprices.shared.db.data_session import SessionFactory


class JobSessionFactory(SessionFactory):
    def __init__(self, config: Config) -> None:
        self.engine = create_engine(
            f"mysql+pymysql://{config.database.db_user}:{config.database.db_password}@"
            f"{config.database.db_host}/{config.database.db_name}", pool_pre_ping=True)

    def create_session(self) -> Session:
        session_maker = sessionmaker(bind=self.engine)
        return session_maker()

    def create_scoped_session(self) -> Session:
        session_maker = sessionmaker(bind=self.engine)
        return scoped_session(session_maker)()
