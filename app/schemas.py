from pydantic import AnyHttpUrl, BaseModel


class UrlCreate(BaseModel):
    original_url: AnyHttpUrl


class UrlResponse(BaseModel):
    short_code: str
    original_url: str

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
    click_count: int
