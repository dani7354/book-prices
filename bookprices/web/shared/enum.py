from enum import StrEnum, IntEnum


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"


class HttpStatusCode(IntEnum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
