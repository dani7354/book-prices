from datetime import datetime

import pytest

from bookprices.shared.db.tables import BookList
from bookprices.shared.repository.booklist import BookListRepository


@pytest.fixture
def booklist_repository(data_session) -> BookListRepository:
    return BookListRepository(data_session)


@pytest.fixture
def booklist() -> BookList:
    return BookList(
        user_id="0000",
        name="TestBookList 0",
        description="A test book list",
        updated=datetime.now(),
        created=datetime.now())


def test_create_and_list_booklist(
        booklist_repository: BookListRepository,
        booklist: BookList) -> None:
    booklist_repository.add(booklist)
    booklist_repository._session.commit()

    booklist_list = booklist_repository.list_for_user(booklist.user_id)

    assert booklist_list
    first = booklist_list[0]
    assert first.id == 1
    assert first.name == booklist.name
    assert first.description == booklist.description


def test_update_booklist(
        booklist_repository: BookListRepository,
        booklist: BookList) -> None:
    booklist_repository.add(booklist)
    booklist_repository._session.commit()

    list_id, new_name = 1, "UpdatedListName"
    item = booklist_repository.get(list_id)
    item.name = new_name
    booklist_repository.update(item)
    booklist_repository._session.commit()

    updated = booklist_repository.get(list_id)
    assert updated.name == new_name


def test_delete_booklist(
        booklist_repository: BookListRepository,
        booklist: BookList) -> None:
    booklist_repository.add(booklist)
    booklist_repository._session.commit()
    assert booklist_repository.list_for_user(booklist.user_id)

    booklist_repository.delete(1)
    booklist_repository._session.commit()
    assert not booklist_repository.get_list()
