import httpx
from app.config import settings


class OverpassClient:
    def __init__(self, base_url: str | None = None, timeout_ms: int | None = None):
        self.base_url = base_url or settings.overpass_base_url
        self.timeout = (timeout_ms or settings.overpass_timeout_ms) / 1000.0
        self.client = httpx.Client(timeout=self.timeout)

    def query(self, query_text: str) -> dict:
        response = self.client.post(self.base_url, data=query_text)
        response.raise_for_status()
        return response.json()
