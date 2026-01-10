from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class SessionFactory(ABC):
    """ Abstract base class for creating database sessions."""
    @abstractmethod
    def create_session(self) -> Session:
        raise NotImplementedError
