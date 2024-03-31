import logging
from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record) -> str:
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

    @staticmethod
    def get_formatter() -> "RequestFormatter":
        return RequestFormatter(
            "[%(asctime)s] %(remote_addr)s requested %(url)s %(levelname)s in %(module)s: %(message)s")
