import json
from typing import Any

import httpx
from app.config import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.client = httpx.Client(timeout=10.0)

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.0,
        }
        response = self.client.post(f"{self.base_url}/v1/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            return data["choices"][0].get("text", "")
        return json.dumps({})
