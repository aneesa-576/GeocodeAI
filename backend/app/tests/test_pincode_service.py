import pandas as pd
from app.models.address import ParsedAddress
from app.services.pincode_service import PincodeResult, PincodeService


def test_pincode_service_loads_dataset(monkeypatch, tmp_path):
    df = pd.DataFrame(
        {
            "pincode": ["560038"],
            "state_name": ["Karnataka"],
            "district_name": ["Bangalore Urban"],
            "office_name": ["Bangalore"],
            "latitude": [12.9716],
            "longitude": [77.5946],
        }
    )
    csv_path = tmp_path / "pincode.csv"
    df.to_csv(csv_path, index=False)
    monkeypatch.setenv("PINCODE_CSV_PATH", str(csv_path))

    service = PincodeService()
    parsed = ParsedAddress(
        pincode="560038", state="Karnataka", district="Bangalore Urban"
    )
    result = service.verify(parsed)

    assert result.matched_pincode == "560038"
    assert result.centroid["lat"] == 12.9716
    assert not result.conflict
