from app.models.address import ParsedAddress
from app.services.landmark_service import LandmarkResult
from app.services.pincode_service import PincodeResult


class GeocodingService:
    def generate(
        self,
        parsed: ParsedAddress,
        pincode_result: PincodeResult,
        landmark_result: LandmarkResult,
    ) -> dict | None:
        if landmark_result.candidates:
            return landmark_result.candidates[0]
        if pincode_result.centroid:
            return {
                "lat": pincode_result.centroid["lat"],
                "lon": pincode_result.centroid["lon"],
                "precision": "pincode",
            }
        return None
