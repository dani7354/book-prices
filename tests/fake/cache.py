from bookprices.shared.cache.client import CacheClient


class FakeCacheClient(CacheClient):
    def delete_key(self, key: str) -> None:
        pass

    def delete_keys(self, keys: list[str]) -> None:
        pass
