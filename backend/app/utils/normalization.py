import re
import unicodedata

ABBREVIATIONS = {
    "rd": "road",
    "st": "street",
    "bldg": "building",
    "blk": "block",
    "col": "colony",
    "opp": "opposite",
    "near": "near",
    "nr": "near",
    "no": "number",
}

LANDMARK_RELATIONS = [
    "opposite",
    "near",
    "beside",
    "behind",
    "in front of",
    "next to",
    "inside",
]


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", value).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    return text


def normalize_component(value: str | None) -> str:
    if not value:
        return ""
    text = normalize_text(value.lower())
    text = re.sub(r"[^\w\s\-&,']+", " ", text)
    text = re.sub(
        r"\b(" + "|".join(re.escape(k) for k in ABBREVIATIONS) + r")\b",
        lambda m: ABBREVIATIONS[m.group(1)],
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def extract_pincode(text: str) -> str | None:
    match = re.search(r"\b(\d{6})\b", text)
    return match.group(1) if match else None


def find_landmark_relation(text: str) -> str | None:
    normalized = normalize_text(text.lower())
    for rel in LANDMARK_RELATIONS:
        if rel in normalized:
            return rel
    return "unknown"
