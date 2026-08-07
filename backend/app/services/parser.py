import json
import re
from typing import Any

from app.infrastructure.ollama_client import OllamaClient
from app.models.address import ParsedAddress
from app.utils.language import detect_language, detect_script
from app.utils.normalization import (
    extract_pincode,
    find_landmark_relation,
    normalize_text,
)
from pydantic import ValidationError

ADDRESS_PROMPT = """You are a structured address parser for Indian delivery addresses. Return valid JSON only with these fields: house_number, building, floor, street, road, colony, locality, landmark, landmark_relation, city, district, state, pincode, country, language, script.
Parse the address: "{address}"
If a field is missing, use null.
"""

from app.config import settings


class AddressParserService:
    def __init__(self):
        self.provider = settings.parser_provider.lower()
        self.client = OllamaClient()

    def parse(self, address: str) -> ParsedAddress:
        normalized_address = normalize_text(address)
        if self.provider == "ollama":
            parsed = self._ollama_parse(normalized_address)
            if parsed is not None:
                return parsed
        return self._fallback_parse(normalized_address)

    def _ollama_parse(self, address: str) -> ParsedAddress | None:
        prompt = ADDRESS_PROMPT.format(address=address)
        try:
            raw = self.client.generate(prompt)
            parsed = self._validate_json(raw)
            if parsed:
                return parsed
            correction_prompt = (
                prompt + "\nRespond again with strictly valid JSON matching the schema."
            )
            raw2 = self.client.generate(correction_prompt)
            parsed2 = self._validate_json(raw2)
            return parsed2
        except Exception:
            return None

    def _validate_json(self, payload: str) -> ParsedAddress | None:
        try:
            data = json.loads(payload)
            if not isinstance(data, dict):
                return None
            if "country" not in data:
                data["country"] = "India"
            if "language" not in data or not data["language"]:
                data["language"] = detect_language(payload)
            if "script" not in data or not data["script"]:
                data["script"] = detect_script(payload)
            return ParsedAddress(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def _fallback_parse(self, address: str) -> ParsedAddress:
        pincode = extract_pincode(address)
        parts = re.split(r"[,:\n]", address)
        cleaned = [p.strip() for p in parts if p.strip()]
        parsed = ParsedAddress()
        parsed.country = "India"
        parsed.language = detect_language(address)
        parsed.script = detect_script(address)
        parsed.pincode = pincode
        if cleaned:
            parsed.landmark = cleaned[0] if len(cleaned) == 1 else cleaned[-2]
            parsed.locality = cleaned[-1]
            if len(cleaned) >= 3:
                parsed.city = cleaned[-2]
            if len(cleaned) >= 4:
                parsed.district = cleaned[-3]
        parsed.landmark_relation = find_landmark_relation(address)
        return parsed
