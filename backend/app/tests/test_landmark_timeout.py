from app.models.address import ParsedAddress
from app.services.landmark_service import LandmarkService
from app.services.pincode_service import PincodeResult


class DummyPincodeResult(PincodeResult):
    def __init__(self):
        super().__init__()
        self.centroid = {"lat": 12.9716, "lon": 77.5946}
        self.matched_pincode = "560038"


def test_landmark_service_handles_overpass_failures(monkeypatch):
    service = LandmarkService()
    parsed = ParsedAddress(landmark="MG Road", city="Bangalore")
    pincode_result = DummyPincodeResult()

    def raise_error(query):
        raise RuntimeError("Overpass down")

    monkeypatch.setattr(service.client, "query", raise_error)
    result = service.find_landmarks(parsed, pincode_result)
    assert result.candidates == []
    assert result.matched is None
