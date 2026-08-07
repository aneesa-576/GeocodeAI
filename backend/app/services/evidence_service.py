from app.models.address import ParsedAddress
from app.services.landmark_service import LandmarkResult
from app.services.pincode_service import PincodeResult


class EvidenceService:
    def collect(
        self,
        parsed: ParsedAddress,
        pincode_result: PincodeResult,
        landmark_result: LandmarkResult,
        candidate: dict | None,
    ) -> list[dict]:
        evidence = []
        if pincode_result.matched_pincode:
            evidence.append(
                {
                    "type": "PINCODE_MATCH",
                    "description": "Pincode matched to reference centroid.",
                    "details": {
                        "requested_pincode": pincode_result.requested_pincode,
                        "matched_pincode": pincode_result.matched_pincode,
                        "state": pincode_result.state,
                        "district": pincode_result.district,
                    },
                }
            )
        if pincode_result.conflict:
            evidence.append(
                {
                    "type": "CONFLICT",
                    "description": "Parsed pincode and administrative region conflict detected.",
                    "details": {"corrections": pincode_result.corrections},
                }
            )
        if landmark_result.candidates:
            best = landmark_result.candidates[0]
            evidence.append(
                {
                    "type": "LANDMARK_MATCH",
                    "description": "Landmark verified using OSM Overpass results.",
                    "details": {
                        "landmark": parsed.landmark,
                        "matched_name": best["name"],
                        "score": best["score"],
                    },
                }
            )
        if candidate:
            evidence.append(
                {
                    "type": "CANDIDATE_SELECTION",
                    "description": "Location candidate selected based on weighted evidence.",
                    "details": {
                        "source": candidate.get("source"),
                        "precision": candidate.get("precision"),
                    },
                }
            )
        return evidence
