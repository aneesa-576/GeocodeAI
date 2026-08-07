import json
import re
import logging
from pydantic import ValidationError
from app.models.address import ParsedAddress
from app.infrastructure.ollama_client import OllamaClient
from app.utils.language import detect_language, detect_script
from app.utils.normalization import normalize_text, extract_pincode, find_landmark_relation
from app.config import settings

logger = logging.getLogger(__name__)

ADDRESS_PROMPT = '''You are a structured address parser for Indian delivery addresses. Return valid JSON only with these fields: house_number, building, floor, street, road, colony, locality, landmark, landmark_relation, city, district, state, pincode, country, language, script.
Parse the address: "{address}"
If a field is missing, use null.
'''

class AddressParserService:
    def __init__(self):
        self.provider = settings.parser_provider.lower()
        self.client = OllamaClient()

    async def parse(self, address: str) -> ParsedAddress:
        """
        Asynchronously parses unstructured addresses using local LLM infrastructure 
        with automatic schema-validation recovery and hard deterministic fallbacks.
        """
        normalized_address = normalize_text(address)
        if self.provider == "ollama":
            parsed = await self._ollama_parse(normalized_address)
            if parsed is not None:
                return parsed
        return self._fallback_parse(normalized_address)

    async def _ollama_parse(self, address: str) -> ParsedAddress | None:
        prompt = ADDRESS_PROMPT.format(address=address)
        try:
            raw = await self.client.generate_structured(prompt)
            parsed = self._validate_json(raw, address)
            if parsed:
                return parsed
                
            # If the schema constraint fails, try once more with explicit correction context
            correction_prompt = prompt + "\nRespond again with strictly valid JSON matching the schema fields exactly."
            raw2 = await self.client.generate_structured(correction_prompt)
            return self._validate_json(raw2, address)
        except Exception as e:
            logger.warning(f"Ollama address parsing failed: {str(e)}. Falling back.")
            return None

    def _validate_json(self, payload: str, original_text: str) -> ParsedAddress | None:
        try:
            data = json.loads(payload)
            if not isinstance(data, dict):
                return None
                
            if "country" not in data or not data["country"]:
                data["country"] = "India"
            if "language" not in data or not data["language"]:
                data["language"] = detect_language(original_text)
            if "script" not in data or not data["script"]:
                data["script"] = detect_script(original_text)
                
            return ParsedAddress(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def _fallback_parse(self, address: str) -> ParsedAddress:
        logger.info("Using deterministic regex fallback parser.")
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