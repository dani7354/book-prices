import os
import shutil
from unittest.mock import MagicMock

import pytest
from bookprices.shared.db.book import BookDb
from bookprices.shared.model.book import Book
from bookprices.cronjob.delete_images import DeleteImagesJob, DEFAULT_IMAGE_NAME


@pytest.fixture()
def images(tmpdir):
    """ Provides three fake images to play with! """
    files = [
        os.path.join(tmpdir.strpath, "1.png"),
        os.path.join(tmpdir.strpath, "2.png"),
        os.path.join(tmpdir.strpath, "3.png")
    ]

    for f in files:
        with open(f, "wb") as image_file:
            image_file.write(b"\x00" * 1000)

    yield files

    shutil.rmtree(tmpdir)


@pytest.fixture()
def books(images) -> list[Book]:
    """ Provides books to play with! """
    books = [Book(i, "isbn", "title", "author", os.path.basename(image), None) for i, image in enumerate(images)]

    return books


@pytest.mark.parametrize("images_deleted", [0, 1, 2, 3])
def test_deletes_multiple_images(books, images, tmpdir, images_deleted):
    mock_db = BookDb("", "", "", "", "")
    books_from_db = [books[i] for i in range(0, len(images) - images_deleted)]
    mock_db.get_books = MagicMock(return_value=books_from_db)

    job = DeleteImagesJob(mock_db, tmpdir.strpath)
    job.run()

    images_left = len(os.listdir(tmpdir.strpath))
    expected_images_left = len(images) - images_deleted
    assert expected_images_left == images_left


def test_deletes_only_unused_images(books, images, tmpdir):
    mock_db = BookDb("", "", "", "", "")
    books_from_db = [books[0], books[2]]
    mock_db.get_books = MagicMock(return_value=books_from_db)

    job = DeleteImagesJob(mock_db, tmpdir.strpath)
    job.run()

    images_left = os.listdir(tmpdir.strpath)
    assert books[0].image_url in images_left
    assert books[2].image_url in images_left
    assert books[1].image_url not in images_left


def test_exclude_default_image_from_deletion(books, images, tmpdir):
    mock_db = BookDb("", "", "", "", "")
    mock_db.get_books = MagicMock(return_value=[])
    with open(os.path.join(tmpdir.strpath,DEFAULT_IMAGE_NAME), "wb") as default_image_file:
        default_image_file.write(b"\x00" * 1000)

    job = DeleteImagesJob(mock_db, tmpdir.strpath)
    job.run()

    images_left = os.listdir(tmpdir.strpath)
    assert DEFAULT_IMAGE_NAME in images_left
