import os
from typing import ClassVar


class BookImageFileService:
    """ Service for managing book image files. """
    supported_image_extensions: ClassVar[tuple[str]] = (".jpg", ".jpeg", ".png", ".bmp")

    def __init__(self, image_directory: str) -> None:
        self._image_directory = image_directory

    def get_image_path(self, image_name: str) -> str:
        return os.path.join(self._image_directory, image_name)

    def get_images_available(self) -> list[str]:
        images = [
            x for x in os.listdir(self._image_directory)
            if not x.startswith('.') and x.endswith(self.supported_image_extensions)]

        return sorted(images)

    def save_image(self, image_name: str, image_data: bytes) -> None:
        image_path = self.get_image_path(image_name)
        if self.image_exists(image_path):
            raise FileExistsError(f"Image {image_name} already exists at {image_path}")
        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)

    def delete_image(self, image_name: str) -> None:
        image_path = self.get_image_path(image_name)
        if not self.image_exists(image_name):
            raise FileNotFoundError(f"Image {image_name} does not exist at {image_path}")
        os.remove(image_path)

    def image_exists(self, image_name: str) -> bool:
        image_path = os.path.join(self._image_directory, image_name)
        return os.path.isfile(image_path)
