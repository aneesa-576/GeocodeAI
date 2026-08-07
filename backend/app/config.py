import os

_HAS_PYDANTIC = False
try:
    from pydantic import BaseSettings, Field

    _HAS_PYDANTIC = True
except Exception:
    try:
        from pydantic import Field
        from pydantic_settings import BaseSettings

        _HAS_PYDANTIC = True
    except Exception:
        _HAS_PYDANTIC = False


if _HAS_PYDANTIC:

    class Settings(BaseSettings):
        parser_provider: str = Field("ollama", env="PARSER_PROVIDER")
        ollama_base_url: str = Field("http://127.0.0.1:11434", env="OLLAMA_BASE_URL")
        ollama_model: str = Field("qwen-2.5-3b", env="OLLAMA_MODEL")
        overpass_base_url: str = Field(
            "https://overpass-api.de/api/interpreter", env="OVERPASS_BASE_URL"
        )
        pincode_csv_path: str = Field(
            "./app/data/pincode/all_india_pincode_2025.csv", env="PINCODE_CSV_PATH"
        )
        overpass_timeout_ms: int = Field(250, env="OVERPASS_TIMEOUT_MS")
        cache_ttl_seconds: int = Field(600, env="CACHE_TTL_SECONDS")
        max_location_candidates: int = Field(5, env="MAX_LOCATION_CANDIDATES")

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

    settings = Settings()
else:

    class Settings:
        def __init__(self):
            self.parser_provider = os.getenv("PARSER_PROVIDER", "ollama")
            self.ollama_base_url = os.getenv(
                "OLLAMA_BASE_URL", "http://127.0.0.1:11434"
            )
            self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen-2.5-3b")
            self.overpass_base_url = os.getenv(
                "OVERPASS_BASE_URL", "https://overpass-api.de/api/interpreter"
            )
            self.pincode_csv_path = os.getenv(
                "PINCODE_CSV_PATH", "./app/data/pincode/all_india_pincode_2025.csv"
            )
            self.overpass_timeout_ms = int(os.getenv("OVERPASS_TIMEOUT_MS", "250"))
            self.cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "600"))
            self.max_location_candidates = int(
                os.getenv("MAX_LOCATION_CANDIDATES", "5")
            )

    settings = Settings()
