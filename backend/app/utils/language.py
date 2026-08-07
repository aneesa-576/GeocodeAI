import re

REGIONAL_SCRIPTS = {
    "devanagari": r"[\u0900-\u097F]",
    "bengali": r"[\u0980-\u09FF]",
    "gujarati": r"[\u0A80-\u0AFF]",
    "tamil": r"[\u0B80-\u0BFF]",
    "telugu": r"[\u0C00-\u0C7F]",
    "kannada": r"[\u0C80-\u0CFF]",
    "malayalam": r"[\u0D00-\u0D7F]",
}

SCRIPT_DETECTION_ORDER = list(REGIONAL_SCRIPTS.items())


def detect_script(text: str) -> str:
    for script_name, pattern in SCRIPT_DETECTION_ORDER:
        if re.search(pattern, text):
            return script_name
    return "latin"


def detect_language(text: str) -> str:
    if any(ch.isascii() and ch.isalpha() for ch in text):
        return "english"
    if detect_script(text) != "latin":
        return "regional"
    return "unknown"
