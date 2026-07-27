from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class URLCreate(BaseModel):
    url: str

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
    id: int
    url_id: int
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    is_up: bool
    checked_at: datetime

    class Config:
        from_attributes = True


class URLOut(BaseModel):
    id: int
    url: str
    created_at: datetime
    is_up: Optional[bool] = None
    last_status_code: Optional[int] = None
    last_response_time_ms: Optional[int] = None
    last_checked_at: Optional[datetime] = None

    class Config:
        from_attributes = True
