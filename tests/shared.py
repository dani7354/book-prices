import os
import requests


def mock_get(*args, **kwargs) -> requests.Response:
    fake_response = requests.Response()
    fake_response.status_code = 200
    full_path = os.path.join(os.path.dirname(__file__), "html", "price_format.html")
    with open(full_path, "rb") as html_file:
        fake_response._content = html_file.read()

    return fake_response
