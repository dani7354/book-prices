from flask_caching import Cache
from bookprices.web.settings import DEBUG_MODE, MEMCACHED_SERVER, MEMCACHED_PORT


def _create_cache_config() -> dict:
    if not MEMCACHED_SERVER:
        return {"CACHE_TYPE": "SimpleCache"}
    return {
        "DEBUG": DEBUG_MODE,
        "CACHE_TYPE": "MemcachedCache",
        "CACHE_MEMCACHED_SERVERS": [f"{MEMCACHED_SERVER}:{MEMCACHED_PORT}"],
        "CACHE_DEFAULT_TIMEOUT": 300,
    }


cache = Cache(config=_create_cache_config())
