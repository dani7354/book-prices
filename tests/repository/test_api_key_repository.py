from datetime import datetime

import pytest

from bookprices.shared.db.tables import ApiKey
from bookprices.shared.repository.api_key import ApiKeyRepository


@pytest.fixture
def api_key_repository(data_session) -> ApiKeyRepository:
    return ApiKeyRepository(data_session)


@pytest.fixture
def api_key() -> ApiKey:
    return ApiKey(
        api_name="TestApi",
        api_user="TestUser",
        api_key="secret-token",
        updated=datetime.now())


def test_create_and_list_api_key(api_key_repository: ApiKeyRepository, api_key: ApiKey) -> None:
    api_key_repository.add(api_key)
    api_key_repository._session.commit()

    api_keys = api_key_repository.get_list()

    assert api_keys
    first = api_keys[0]
    assert first.id == 1
    assert first.api_name == api_key.api_name
    assert first.api_user == api_key.api_user
    assert first.api_key == api_key.api_key


def test_get_by_name(api_key_repository: ApiKeyRepository, api_key: ApiKey) -> None:
    api_key_repository.add(api_key)
    api_key_repository._session.commit()

    found = api_key_repository.get_by_name(api_key.api_name)

    assert found
    assert found.api_user == api_key.api_user
    assert found.api_key == api_key.api_key


def test_update_api_key(api_key_repository: ApiKeyRepository, api_key: ApiKey) -> None:
    api_key_repository.add(api_key)
    api_key_repository._session.commit()

    updated_user = "UpdatedUser"
    updated_key = "updated-token"
    entity = api_key_repository.get(1)
    entity.api_user = updated_user
    entity.api_key = updated_key
    entity.updated = datetime.now()
    api_key_repository.update(entity)
    api_key_repository._session.commit()

    refreshed = api_key_repository.get(1)
    assert refreshed.api_user == updated_user
    assert refreshed.api_key == updated_key
    assert refreshed.updated != api_key.updated


def test_delete_api_key(api_key_repository: ApiKeyRepository, api_key: ApiKey) -> None:
    api_key_repository.add(api_key)
    api_key_repository._session.commit()
    assert api_key_repository.get_list()

    api_key_repository.delete(1)
    api_key_repository._session.commit()
    assert not api_key_repository.get_list()
