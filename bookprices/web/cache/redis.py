from flask_caching import Cache
from bookprices.web.settings import DEBUG_MODE, REDIS_SERVER, REDIS_SERVER_PORT, REDIS_DB, CACHE_DEFAULT_TIMEOUT


def _create_cache_config() -> dict:
    if not REDIS_SERVER:
        return {"CACHE_TYPE": "SimpleCache"}
    return {
        "DEBUG": DEBUG_MODE,
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": REDIS_SERVER,
        "CACHE_REDIS_PORT": REDIS_SERVER_PORT,
        "CACHE_REDIS_DB": REDIS_DB,
        "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    }


cache = Cache(config=_create_cache_config())
