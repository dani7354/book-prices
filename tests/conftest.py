from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session, Session

from bookprices.shared.db.data_session import SessionFactory
from bookprices.shared.db.tables import BaseModel


class FakeSessionFactory(SessionFactory):

    def __init__(self, session):
        self._session = session

    @contextmanager
    def create_session(self):
        yield self._session

    def create_scoped_session(self) -> Session:
        return self._session


@pytest.fixture
def data_session():
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    with create_session(engine) as session:
        yield session

    BaseModel.metadata.drop_all(engine)


@pytest.fixture
def session_factory(data_session):
    return FakeSessionFactory(data_session)
