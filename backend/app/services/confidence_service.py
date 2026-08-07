from app.models.address import ParsedAddress
from app.services.landmark_service import LandmarkResult
from app.services.pincode_service import PincodeResult


class ConfidenceService:
    def score(
        self,
        parsed: ParsedAddress,
        pincode_result: PincodeResult,
        landmark_result: LandmarkResult,
        candidate: dict | None,
    ) -> dict:
        score = 0
        evidence = []
        if pincode_result.matched_pincode:
            score += 30
        if parsed.locality:
            score += 20
        if landmark_result.candidates:
            score += 25
        if candidate and candidate.get("precision") == "landmark":
            score += 15
        if pincode_result.conflict:
            score -= 20
        score = max(0, min(100, score))
        if score >= 80:
            band = "HIGH"
        elif score >= 60:
            band = "MEDIUM"
        else:
            band = "LOW"
        return {"score": score, "band": band}
