import logging
import functools
import time
from requests.exceptions import ConnectionError


logger = logging.getLogger(__name__)


class ApiUnavailableError(Exception):
    pass


def retry_on_connection_error(retries: int = 5, sleep_seconds: int = 3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    last_exception = e
                    time.sleep(sleep_seconds)
                    logger.error(
                        "ConnectionError occurred in %s. Retrying %d/%d...",
                        func.__name__, attempt + 1, retries)
            logger.error(
                "Function %s failed after %d retries. Api is unavailable.",
                func.__name__, retries)
            raise ApiUnavailableError from last_exception

        return wrapper
    return decorator