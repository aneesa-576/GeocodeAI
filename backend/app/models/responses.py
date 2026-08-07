from pydantic import BaseModel


class LatLong(BaseModel):
    lat: float
    lon: float
    precision: str


class Confidence(BaseModel):
    score: int
    band: str


class EvidenceItem(BaseModel):
    type: str
    description: str
    details: dict


class CorrectionItem(BaseModel):
    original_component: str
    corrected_component: str
    reason: str


class GeocodeResponse(BaseModel):
    request_id: str
    status: str
    original_address: str
    parsed_address: dict
    location: LatLong | None
    confidence: Confidence
    evidence: list[EvidenceItem]
    corrections: list[CorrectionItem]
    latency_ms: float
    estimated_cost_inr: float


class HealthResponse(BaseModel):
    status: str
    pincode_dataset_loaded: bool
    parser_provider: str
    ollama_available: bool | None = None
