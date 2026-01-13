from abc import ABC, abstractmethod

from sqlalchemy.orm import Session, sessionmaker


class SessionFactory(ABC):
    """ Abstract base class for creating database sessions."""
    @abstractmethod
    def create_session(self) -> Session:
        raise NotImplementedError

    @abstractmethod
    def create_scoped_session(self) -> Session:
        raise NotImplementedError
