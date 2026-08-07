from pydantic import BaseModel, Field


class ParsedAddress(BaseModel):
    house_number: str | None = None
    building: str | None = None
    floor: str | None = None
    street: str | None = None
    road: str | None = None
    colony: str | None = None
    locality: str | None = None
    landmark: str | None = None
    landmark_relation: str | None = "unknown"
    city: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str = Field(default="India")
    language: str | None = None
    script: str | None = None
