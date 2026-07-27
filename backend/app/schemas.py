from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict


class URLCreate(BaseModel):
    url: str
    name: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        # Validate syntax via HttpUrl adapter
        HttpUrl(v)
        return v


class CheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url_id: int
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    is_up: bool
    checked_at: datetime


class URLOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    url: str
    created_at: datetime
    is_up: Optional[bool] = None
    last_status_code: Optional[int] = None
    last_response_time_ms: Optional[float] = None
    last_checked_at: Optional[datetime] = None
    uptime_percentage: Optional[float] = None
    total_checks: int = 0
