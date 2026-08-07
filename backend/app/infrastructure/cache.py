import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self.store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self.store.get(key)
        if not entry:
            return None
        timestamp, value = entry
        if time.time() - timestamp > self.ttl_seconds:
            self.store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self.store[key] = (time.time(), value)

    def clear(self) -> None:
        self.store.clear()
