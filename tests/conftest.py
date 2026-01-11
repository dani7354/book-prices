import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from bookprices.shared.db.tables import BaseModel


@pytest.fixture
def data_session():
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    with create_session(engine) as session:
        yield session

    BaseModel.metadata.drop_all(engine)