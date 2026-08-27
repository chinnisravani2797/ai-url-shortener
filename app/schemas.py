import ipaddress
from datetime import datetime, timezone
from urllib.parse import urlsplit

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

    @field_validator("original_url")
    @classmethod
    def destination_must_be_safe(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        parsed = urlsplit(str(value))
        if parsed.username or parsed.password:
            raise ValueError("URL credentials are not allowed")
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if hostname in {"localhost", "localhost.localdomain"}:
            raise ValueError("Local destinations are not allowed")
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            address = None
        if address and (address.is_private or address.is_loopback or address.is_link_local):
            raise ValueError("Private or local destinations are not allowed")
        return value


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
