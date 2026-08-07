from app.models.address import ParsedAddress
from app.services.pincode_service import PincodeResult


class AuditService:
    def collect_corrections(
        self, parsed: ParsedAddress, pincode_result: PincodeResult
    ) -> list[dict]:
        return pincode_result.corrections or []
