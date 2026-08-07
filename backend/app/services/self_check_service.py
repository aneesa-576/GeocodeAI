from app.models.address import ParsedAddress


class SelfCheckService:
    def validate(
        self, parsed: ParsedAddress, candidate: dict | None, confidence: dict
    ) -> str:
        if candidate is None:
            return "needs_review"
        if confidence["band"] == "LOW":
            return "needs_review"
        if (
            parsed.state
            and candidate.get("source") == "landmark"
            and not parsed.landmark
        ):
            return "needs_review"
        return "ok"
