import json
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        # Strict timeout guard: 3 seconds max for local inference to protect the loop
        self.timeout = httpx.Timeout(3.0, connect=1.0)

    async def generate_structured(self, prompt: str) -> str:
        """
        Calls Ollama's native generation endpoint forcing structured JSON response.
        """
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",  # Hard constraint forcing the local LLM to output valid JSON
            "options": {
                "temperature": 0.0  # Zero out creativity for deterministic parsing
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Native Ollama returns text inside the 'response' key
                return data.get("response", "{}")
            except httpx.TimeoutException:
                logger.error("Ollama inference timed out. Routing immediately to fallback parser.")
                return json.dumps({})
            except Exception as e:
                logger.error(f"Ollama communication failure: {str(e)}")
                return json.dumps({})
            