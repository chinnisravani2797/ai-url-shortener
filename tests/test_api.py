from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app import main
from app.db import SessionLocal
from app.main import app
from app.models import Url

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_readiness():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_create_redirect_and_analytics():
    created = client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.org/interview"},
    )
    assert created.status_code == 201
    short_code = created.json()["short_code"]

    redirected = client.get(f"/{short_code}", follow_redirects=False)
    assert redirected.status_code == 307
    assert redirected.headers["location"] == "https://example.org/interview"

    analytics = client.get(f"/api/v1/urls/{short_code}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["click_count"] == 1


def test_unknown_short_code_returns_404():
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_past_expiry_is_rejected():
    response = client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.org/expired",
            "expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        },
    )
    assert response.status_code == 422


def test_unsafe_destination_is_rejected():
    response = client.post(
        "/api/v1/urls",
        json={"original_url": "http://127.0.0.1/admin"},
    )
    assert response.status_code == 422


def test_oversized_request_is_rejected(monkeypatch):
    monkeypatch.setattr(main.settings, "max_request_bytes", 10)
    response = client.post(
        "/api/v1/urls",
        content='{"original_url":"https://example.org"}',
        headers={"content-type": "application/json", "content-length": "100"},
    )
    assert response.status_code == 413


def test_analytics_api_key_is_enforced_when_configured(monkeypatch):
    created = client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.org/protected"},
    )
    short_code = created.json()["short_code"]
    monkeypatch.setattr(main.settings, "analytics_api_key", "test-key")

    unauthorized = client.get(f"/api/v1/urls/{short_code}/analytics")
    assert unauthorized.status_code == 401

    authorized = client.get(
        f"/api/v1/urls/{short_code}/analytics",
        headers={"X-API-Key": "test-key"},
    )
    assert authorized.status_code == 200


def test_rate_limit_returns_429_when_exceeded(monkeypatch):
    main.rate_limit_state.clear()
    monkeypatch.setattr(main.settings, "rate_limit_per_minute", 1)
    first = client.get("/health")
    second = client.get("/health")
    assert first.status_code == 200
    assert second.status_code == 429


def test_expired_url_returns_410_and_keeps_analytics():
    short_code = f"expired-{uuid4().hex[:8]}"
    db = SessionLocal()
    record = Url(
        short_code=short_code,
        original_url="https://example.org/expired",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1),
    )
    db.add(record)
    db.commit()
    db.close()

    response = client.get(f"/{short_code}")
    assert response.status_code == 410
    analytics = client.get(f"/api/v1/urls/{short_code}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["click_count"] == 0
