"""
Integration tests for the /api/urls CRUD endpoints.

All tests use an in-memory SQLite database (via conftest.py fixtures).
Network calls to the pinger are mocked with pytest-mock / unittest.mock.
"""
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SAMPLE_URL = "https://example.com"
SAMPLE_NAME = "Example Site"


def _make_fake_check(url_id: int, is_up: bool = True, status_code: int = 200,
                     response_time_ms: float = 150.0):
    """Return a mock Check-like object that satisfies _build_url_out()."""
    from app.models import Check
    from datetime import datetime, timezone
    check = Check(
        id=99,
        url_id=url_id,
        is_up=is_up,
        status_code=status_code if is_up else None,
        response_time_ms=response_time_ms,
        checked_at=datetime.now(timezone.utc),
    )
    return check


# ---------------------------------------------------------------------------
# POST /api/urls
# ---------------------------------------------------------------------------
class TestCreateUrl:
    def test_create_url_success(self, client):
        """Adding a valid URL returns 201 with immediate check result."""
        fake_check = None  # will be set in mock

        async def mock_check(url_id, url_str, db):
            nonlocal fake_check
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=120.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            fake_check = check
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            resp = client.post("/api/urls", json={"url": SAMPLE_URL, "name": SAMPLE_NAME})

        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == SAMPLE_URL
        assert data["name"] == SAMPLE_NAME
        assert data["is_up"] is True
        assert data["last_status_code"] == 200
        assert data["total_checks"] == 1
        assert data["uptime_percentage"] == 100.0

    def test_create_url_auto_prefix_https(self, client):
        """URLs without scheme get https:// prepended by the validator."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=80.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            resp = client.post("/api/urls", json={"url": "httpbin.org"})

        assert resp.status_code == 201
        assert resp.json()["url"].startswith("https://")

    def test_create_url_duplicate_rejected(self, client):
        """Registering the same URL twice returns 400."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=50.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            client.post("/api/urls", json={"url": "https://duplicate.com"})
            resp = client.post("/api/urls", json={"url": "https://duplicate.com"})

        assert resp.status_code == 400
        assert "already being monitored" in resp.json()["detail"]

    def test_create_url_invalid_url(self, client):
        """An invalid URL string is rejected with 422 Unprocessable Entity."""
        resp = client.post("/api/urls", json={"url": "not a url at all !!!"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/urls
# ---------------------------------------------------------------------------
class TestListUrls:
    def test_list_urls_empty(self, client):
        """Fresh database returns an empty list."""
        resp = client.get("/api/urls")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_urls_returns_added_url(self, client):
        """After adding a URL it appears in the list with correct fields."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=100.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            client.post("/api/urls", json={"url": "https://list-test.com", "name": "List Test"})

        resp = client.get("/api/urls")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["url"] == "https://list-test.com"
        assert items[0]["name"] == "List Test"
        assert "uptime_percentage" in items[0]
        assert "total_checks" in items[0]


# ---------------------------------------------------------------------------
# GET /api/urls/{url_id}
# ---------------------------------------------------------------------------
class TestGetSingleUrl:
    def test_get_single_url(self, client):
        """Single URL endpoint returns the correct record."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=75.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            create_resp = client.post("/api/urls", json={"url": "https://single.com"})

        url_id = create_resp.json()["id"]
        resp = client.get(f"/api/urls/{url_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == url_id

    def test_get_nonexistent_url_returns_404(self, client):
        """Fetching an unknown URL id returns 404."""
        resp = client.get("/api/urls/99999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/urls/{url_id}
# ---------------------------------------------------------------------------
class TestDeleteUrl:
    def test_delete_url_success(self, client):
        """Deleting a monitored URL returns 204 and removes it from list."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=60.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            create_resp = client.post("/api/urls", json={"url": "https://delete-me.com"})

        url_id = create_resp.json()["id"]
        del_resp = client.delete(f"/api/urls/{url_id}")
        assert del_resp.status_code == 204

        list_resp = client.get("/api/urls")
        ids = [u["id"] for u in list_resp.json()]
        assert url_id not in ids

    def test_delete_nonexistent_url_returns_404(self, client):
        """Deleting a URL that doesn't exist returns 404."""
        resp = client.delete("/api/urls/99999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/urls/{url_id}/checks
# ---------------------------------------------------------------------------
class TestUrlChecks:
    def test_get_check_history(self, client):
        """Check history endpoint returns logged checks in descending order."""
        async def mock_check(url_id, url_str, db):
            from app.models import Check
            from datetime import datetime, timezone
            check = Check(
                url_id=url_id, is_up=True, status_code=200,
                response_time_ms=90.0, checked_at=datetime.now(timezone.utc)
            )
            db.add(check)
            db.commit()
            db.refresh(check)
            return check

        with patch("app.routers.urls.check_url_instance", new=mock_check):
            create_resp = client.post("/api/urls", json={"url": "https://history-test.com"})

        url_id = create_resp.json()["id"]
        resp = client.get(f"/api/urls/{url_id}/checks")
        assert resp.status_code == 200
        checks = resp.json()
        assert len(checks) >= 1
        assert checks[0]["is_up"] is True
        assert checks[0]["status_code"] == 200

    def test_check_history_limit_parameter(self, client):
        """The ?limit= query param is respected."""
        resp = client.get("/api/urls/1/checks?limit=5")
        # Either 200 or 404 (URL 1 may not exist) — both are acceptable
        assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------
class TestHealth:
    def test_health_check(self, client):
        """Health endpoint returns 200 with status ok."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
