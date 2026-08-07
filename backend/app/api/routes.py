from app.config import settings
from app.models.requests import GeocodeRequest
from app.models.responses import GeocodeResponse, HealthResponse
from app.services.audit_service import AuditService
from app.services.confidence_service import ConfidenceService
from app.services.evidence_service import EvidenceService
from app.services.geocoding_service import GeocodingService
from app.services.landmark_service import LandmarkService
from app.services.matching_service import MatchingService
from app.services.parser import AddressParserService
from app.services.pincode_service import PincodeService
from app.services.self_check_service import SelfCheckService
from app.utils.timing import Timer
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.post("/api/v1/geocode", response_model=GeocodeResponse)
def geocode(request: GeocodeRequest):
    timer = Timer()
    timer.start("total")

    parser_service = AddressParserService()
    parsed = parser_service.parse(request.address)
    timer.stop("parse")

    pincode_service = PincodeService()
    pincode_result = pincode_service.verify(parsed)
    timer.stop("pincode")

    landmark_service = LandmarkService()
    landmark_result = landmark_service.find_landmarks(parsed, pincode_result)
    timer.stop("landmark")

    matching_service = MatchingService()
    candidate = matching_service.rank_candidates(
        parsed, pincode_result, landmark_result
    )
    timer.stop("matching")

    evidence_service = EvidenceService()
    evidence = evidence_service.collect(
        parsed, pincode_result, landmark_result, candidate
    )
    timer.stop("evidence")

    confidence_service = ConfidenceService()
    confidence = confidence_service.score(
        parsed, pincode_result, landmark_result, candidate
    )
    timer.stop("confidence")

    audit_service = AuditService()
    corrections = audit_service.collect_corrections(parsed, pincode_result)

    self_check = SelfCheckService()
    status = self_check.validate(parsed, candidate, confidence)

    timer.stop("total")
    latency_ms = timer.total_ms()

    location = None
    if candidate:
        location = {
            "lat": candidate["lat"],
            "lon": candidate["lon"],
            "precision": candidate.get("precision", "pincode"),
        }

    return GeocodeResponse(
        request_id=request.request_id or "",
        status=status,
        original_address=request.address,
        parsed_address=parsed.model_dump(),
        location=location,
        confidence=confidence,
        evidence=evidence,
        corrections=corrections,
        latency_ms=latency_ms,
        estimated_cost_inr=timer.cost_inr(),
    )


@router.get("/health", response_model=HealthResponse)
def health():
    pincode_service = PincodeService()
    return HealthResponse(
        status="ok",
        pincode_dataset_loaded=pincode_service.loaded,
        parser_provider=settings.parser_provider,
        ollama_available=None,
    )
