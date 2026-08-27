import secrets
import string

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Url
from .schemas import AnalyticsResponse, UrlCreate, UrlResponse

app = FastAPI(
    title="AI-Assisted URL Shortener",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/urls", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(payload: UrlCreate, db: Session = Depends(get_db)) -> Url:
    alphabet = string.ascii_letters + string.digits
    for _ in range(5):
        code = "".join(secrets.choice(alphabet) for _ in range(7))
        if db.query(Url).filter(Url.short_code == code).first() is None:
            record = Url(short_code=code, original_url=str(payload.original_url))
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
    raise HTTPException(status_code=503, detail="Could not allocate a short code")


@app.get("/api/v1/urls/{short_code}/analytics", response_model=AnalyticsResponse)
def get_analytics(short_code: str, db: Session = Depends(get_db)) -> AnalyticsResponse:
    record = db.query(Url).filter(Url.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return AnalyticsResponse(
        short_code=record.short_code,
        original_url=record.original_url,
        created_at=record.created_at.isoformat(),
        click_count=record.click_count,
    )


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    record = db.query(Url).filter(Url.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    record.click_count += 1
    db.commit()
    return RedirectResponse(url=record.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
