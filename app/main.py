import hmac
import json
import logging
import secrets
import string
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text, update
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, engine, get_db
from .models import Url
from .schemas import AnalyticsResponse, UrlCreate, UrlResponse

app = FastAPI(
    title="AI-Assisted URL Shortener",
    version="0.1.0",
)

logger = logging.getLogger("url_shortener")
logging.basicConfig(level=logging.INFO, format="%(message)s")
settings = get_settings()
rate_limit_state: dict[str, deque[float]] = defaultdict(deque)
rate_limit_lock = Lock()


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    client_key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with rate_limit_lock:
        requests = rate_limit_state[client_key]
        while requests and now - requests[0] >= 60:
            requests.popleft()
        if len(requests) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        requests.append(now)
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(json.dumps({
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }))
    response.headers["X-Request-ID"] = request_id
    return response

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:  # noqa: B008
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.post("/api/v1/urls", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(payload: UrlCreate, db: Session = Depends(get_db)) -> Url:  # noqa: B008
    alphabet = string.ascii_letters + string.digits
    for _ in range(5):
        code = "".join(secrets.choice(alphabet) for _ in range(7))
        if db.query(Url).filter(Url.short_code == code).first() is None:
            record = Url(
                short_code=code,
                original_url=str(payload.original_url),
                expires_at=payload.expires_at,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
    raise HTTPException(status_code=503, detail="Could not allocate a short code")


@app.get("/api/v1/urls/{short_code}/analytics", response_model=AnalyticsResponse)
def get_analytics(
    short_code: str,
    db: Session = Depends(get_db),  # noqa: B008
    api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> AnalyticsResponse:
    if settings.analytics_api_key and not api_key:
        raise HTTPException(status_code=401, detail="Valid API key required")
    if settings.analytics_api_key and not hmac.compare_digest(api_key, settings.analytics_api_key):
        raise HTTPException(status_code=401, detail="Valid API key required")
    record = db.query(Url).filter(Url.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return AnalyticsResponse(
        short_code=record.short_code,
        original_url=record.original_url,
        created_at=record.created_at.isoformat(),
        click_count=record.click_count,
        expires_at=record.expires_at,
    )


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:  # noqa: B008
    record = db.query(Url).filter(Url.short_code == short_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    if record.expires_at is not None and record.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=410, detail="Short URL has expired")
    db.execute(
        update(Url)
        .where(Url.id == record.id)
        .values(click_count=Url.click_count + 1)
    )
    db.commit()
    return RedirectResponse(url=record.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
