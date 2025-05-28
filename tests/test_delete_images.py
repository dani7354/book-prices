import os
import shutil
import pytest
from unittest.mock import MagicMock

from bookprices.shared.config.config import Config
from bookprices.shared.db.database import Database
from bookprices.job.job.delete_images import DeleteImagesJob
from bookprices.shared.service.book_image_file_service import BookImageFileService


@pytest.fixture
def config(tmpdir) -> Config:
    """ Provides a config object with a temporary directory. """
    log_dir = os.path.join(tmpdir.strpath, "logs")
    os.makedirs(log_dir, exist_ok=True)

    image_dir = os.path.join(tmpdir.strpath, "images")
    os.makedirs(image_dir, exist_ok=True)
    return Config(
        database=MagicMock(),
        cache=MagicMock(),
        job_api=MagicMock(),
        loglevel="DEBUG",
        imgdir=image_dir,
        logdir=tmpdir.strpath)


@pytest.fixture
def book_image_file_service(config) -> BookImageFileService:
    """ Provides a BookImageFileService instance """
    return BookImageFileService(config.imgdir)


@pytest.fixture
def images(config):
    """ Provides three fake images to play with! """
    image_dir = config.imgdir
    os.makedirs(image_dir, exist_ok=True)
    files = [
        os.path.join(image_dir, "1.png"),
        os.path.join(image_dir, "2.png"),
        os.path.join(image_dir, "3.png")
    ]

    for f in files:
        with open(f, "wb") as image_file:
            image_file.write(b"\x00" * 1000)

    yield files

    shutil.rmtree(image_dir)


@pytest.mark.parametrize("images_deleted", [0, 1, 2, 3])
def test_deletes_multiple_images(config, images, images_deleted, book_image_file_service) -> None:
    mock_db = Database("", "", "", "", "")
    book_image_urls_from_db = [os.path.basename(images[i]) for i in range(0, len(images) - images_deleted)]
    mock_db.book_db.get_book_image_urls = MagicMock(return_value=book_image_urls_from_db)

    job = DeleteImagesJob(config, mock_db, book_image_file_service)
    job.start()

    images_left = len(os.listdir(config.imgdir))
    expected_images_left = len(images) - images_deleted
    assert expected_images_left == images_left


def test_deletes_only_unused_images(config, images, book_image_file_service) -> None:
    mock_db = Database("", "", "", "", "")
    books_from_db = [os.path.basename(images[0]), os.path.basename(images[2])]
    mock_db.book_db.get_book_image_urls = MagicMock(return_value=books_from_db)

    job = DeleteImagesJob(config, mock_db, book_image_file_service)
    job.start()

    images_left = os.listdir(config.imgdir)
    assert os.path.basename(images[0]) in images_left
    assert os.path.basename(images[2]) in images_left
    assert os.path.basename(images[1]) not in images_left


def test_excludes_default_image_from_deletion(config, book_image_file_service) -> None:
    mock_db = Database("", "", "", "", "")
    mock_db.book_db.get_book_image_urls = MagicMock(return_value=[])
    with open(os.path.join(config.imgdir, DeleteImagesJob.default_image_name), "wb") as default_image_file:
        default_image_file.write(b"\x00" * 1000)

    job = DeleteImagesJob(config, mock_db, book_image_file_service)
    job.start()

    images_left = os.listdir(config.imgdir)
    assert job.default_image_name in images_left
