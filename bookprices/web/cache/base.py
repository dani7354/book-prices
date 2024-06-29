from typing import Any


class BaseCache:
    def get(self, key: str) -> Any:
        pass

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        pass
