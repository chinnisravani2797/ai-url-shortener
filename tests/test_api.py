from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
