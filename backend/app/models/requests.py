from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    address: str = Field(..., min_length=3, max_length=512)
    request_id: str | None = None
