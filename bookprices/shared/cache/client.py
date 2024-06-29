from redis import Redis


class CacheClient:
    def delete_key(self, key: str) -> None:
        raise NotImplementedError

    def delete_keys(self, keys: list[str]) -> None:
        raise NotImplementedError


class RedisClient(CacheClient):
    def __init__(self, host, port=6379):
        self.redis = Redis(host=host, port=port)

    def delete_key(self, key: str) -> None:
        self.redis.delete(key)

    def delete_keys(self, keys: list[str]) -> None:
        self.redis.delete(*keys)
