from app.models.address import ParsedAddress
from app.services.landmark_service import LandmarkResult
from app.services.pincode_service import PincodeResult
from app.utils.distance import haversine_distance
from app.utils.normalization import normalize_component


class MatchingService:
    def rank_candidates(
        self,
        parsed: ParsedAddress,
        pincode_result: PincodeResult,
        landmark_result: LandmarkResult,
    ) -> dict | None:
        candidates = []
        if pincode_result.centroid:
            candidates.append(
                {
                    "source": "pincode_centroid",
                    "lat": pincode_result.centroid["lat"],
                    "lon": pincode_result.centroid["lon"],
                    "score": 50,
                    "precision": "pincode",
                }
            )
        if landmark_result.candidates:
            best = landmark_result.candidates[0]
            rel = parsed.landmark_relation or "unknown"
            adjustment = 0.0
            if rel == "near":
                adjustment = 0.0002
            candidates.append(
                {
                    "source": "landmark",
                    "lat": best["lat"] + adjustment,
                    "lon": best["lon"] + adjustment,
                    "score": best["score"],
                    "precision": "landmark",
                    "landmark_name": best["name"],
                }
            )
        if parsed.locality and pincode_result.centroid:
            candidates.append(
                {
                    "source": "locality_centroid",
                    "lat": pincode_result.centroid["lat"],
                    "lon": pincode_result.centroid["lon"],
                    "score": 30,
                    "precision": "locality",
                }
            )
        if not candidates:
            return None
        top = max(candidates, key=lambda c: c["score"])
        return top
