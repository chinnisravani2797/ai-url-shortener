from datetime import datetime, timezone

from pydantic import AnyHttpUrl, BaseModel, field_validator


class UrlCreate(BaseModel):
    original_url: AnyHttpUrl
    expires_at: datetime | None = None

    @field_validator("expires_at")
    @classmethod
    def expiry_must_be_in_future(cls, value: datetime | None) -> datetime | None:
        now = datetime.now(timezone.utc)
        if value is not None and value <= now:
            raise ValueError("expires_at must be in the future")
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value is not None else None


class UrlResponse(BaseModel):
    short_code: str
    original_url: str
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    click_count: int
    expires_at: datetime | None = None
