from bookprices.shared.cache.client import CacheClient


class FakeCacheClient(CacheClient):
    def delete_key(self, key: str) -> None:
        pass  # Do nothing, cache is fake

    def delete_keys(self, keys: list[str]) -> None:
        pass  # Do nothing, cache is fake
