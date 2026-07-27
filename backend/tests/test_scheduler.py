"""
Unit tests for the async HTTP pinger engine (scheduler.py).

All real HTTP calls are intercepted by httpx's MockTransport — no network
access is needed.

Fix: We patch "app.scheduler.httpx.AsyncClient" (the reference inside the
scheduler module) and use _RealAsyncClient saved before patching so the
lambda never calls the mock recursively.
"""
import pytest
import httpx
from unittest.mock import MagicMock, patch

from app.scheduler import check_url_instance

# Save a reference to the REAL AsyncClient before any patching happens.
# This prevents the RecursionError caused by the lambda calling the mock
# when we patch httpx.AsyncClient globally.
_RealAsyncClient = httpx.AsyncClient


# ---------------------------------------------------------------------------
# Helpers — mock DB session
# ---------------------------------------------------------------------------
def _make_mock_db():
    """Return a MagicMock that behaves like a SQLAlchemy Session."""
    db = MagicMock()

    def _refresh(obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = 1

    db.refresh.side_effect = _refresh
    return db


def _make_client(transport, **extra):
    """Create a real AsyncClient with the given transport and optional kwargs."""
    return _RealAsyncClient(transport=transport, **extra)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestCheckUrlInstance:

    @pytest.mark.asyncio
    async def test_successful_check_marks_up(self):
        """A 200 response is recorded as is_up=True with a status_code."""
        transport = httpx.MockTransport(lambda r: httpx.Response(200))
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://example.com", db)

        assert result.is_up is True
        assert result.status_code == 200
        assert result.response_time_ms is not None
        assert result.url_id == 1
        db.add.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_404_response_marks_down(self):
        """A 404 response is NOT < 400, so is_up should be False."""
        transport = httpx.MockTransport(lambda r: httpx.Response(404))
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://example.com/notfound", db)

        assert result.is_up is False
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_301_marks_up(self):
        """A 301 response (< 400) is treated as UP."""
        transport = httpx.MockTransport(
            lambda r: httpx.Response(301, headers={"location": "https://example.com/"})
        )
        db = _make_mock_db()

        # Disable follow_redirects so the 301 is returned as-is to be checked
        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(
                transport, timeout=kw.get("timeout", 5.0), follow_redirects=False
            ),
        ):
            result = await check_url_instance(1, "https://example.com", db)

        assert result.status_code == 301
        assert result.is_up is True  # 301 < 400

    @pytest.mark.asyncio
    async def test_timeout_marks_down(self):
        """A timeout exception is recorded as is_up=False, status_code=None."""

        def timeout_transport(request):
            raise httpx.TimeoutException("timed out", request=request)

        transport = httpx.MockTransport(timeout_transport)
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://example.com", db)

        assert result.is_up is False
        assert result.status_code is None
        assert result.response_time_ms is not None

    @pytest.mark.asyncio
    async def test_connection_error_marks_down(self):
        """A DNS/connection failure is recorded as is_up=False."""

        def connect_error_transport(request):
            raise httpx.ConnectError("name resolution failed", request=request)

        transport = httpx.MockTransport(connect_error_transport)
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://invalid.local", db)

        assert result.is_up is False
        assert result.status_code is None

    @pytest.mark.asyncio
    async def test_response_time_is_positive(self):
        """Response time in ms should always be a non-negative float."""
        transport = httpx.MockTransport(lambda r: httpx.Response(200))
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://example.com", db)

        assert isinstance(result.response_time_ms, float)
        assert result.response_time_ms >= 0

    @pytest.mark.asyncio
    async def test_check_persists_to_db(self):
        """Ensure db.add, db.commit, db.refresh are called exactly once."""
        transport = httpx.MockTransport(lambda r: httpx.Response(200))
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            await check_url_instance(2, "https://persist-test.com", db)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_server_error_500_marks_down(self):
        """A 500 response (>= 400) is treated as DOWN."""
        transport = httpx.MockTransport(lambda r: httpx.Response(500))
        db = _make_mock_db()

        with patch(
            "app.scheduler.httpx.AsyncClient",
            side_effect=lambda **kw: _make_client(transport, timeout=kw.get("timeout", 5.0)),
        ):
            result = await check_url_instance(1, "https://example.com", db)

        assert result.is_up is False
        assert result.status_code == 500
