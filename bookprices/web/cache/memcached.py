import pylibmc
from flask_caching import Cache
from bookprices.web.settings import DEBUG_MODE, MEMCACHED_SERVER, MEMCACHED_PORT


class MemcachedClient(pylibmc.Client):
    DEFAULT_TIMEOUT = 300

    def __init__(self, app, config, args, kwargs):
        super().__init__(servers=config["CACHE_MEMCACHED_SERVERS"],
                         binary=True,
                         behaviors=config["CACHE_OPTIONS"])

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, **kwargs):
        kwargs["time"] = timeout  # set method from base class uses "time" instead of "timeout" as kwarg

        return super().set(key, value, **kwargs)

    @classmethod
    def factory(cls, app, config, args, kwargs):
        return MemcachedClient(app, config, args, kwargs)


def _create_cache_config() -> dict:
    if not MEMCACHED_SERVER:
        return {"CACHE_TYPE": "SimpleCache"}
    return {
        "DEBUG": DEBUG_MODE,
        "CACHE_TYPE": "bookprices.web.cache.memcahed.MemcachedClient",
        "CACHE_MEMCACHED_SERVERS": [f"{MEMCACHED_SERVER}:{MEMCACHED_PORT}"],
        "CACHE_OPTIONS": {"tcp_nodelay": True},
        "CACHE_DEFAULT_TIMEOUT": 300,
    }


cache = Cache(config=_create_cache_config())
