import os
import requests


def _create_fake_response(html_file: str) -> requests.Response:
    fake_response = requests.Response()
    fake_response.status_code = 200
    full_path = os.path.join(os.path.dirname(__file__), "html", html_file)
    with open(full_path, "rb") as html_file:
        fake_response._content = html_file.read()

    return fake_response


def mock_get_price(*args, **kwargs) -> requests.Response:
    return _create_fake_response("price_format.html")


def mock_get_image(*args, **kwargs) -> requests.Response:
    return _create_fake_response("image.html")
