"""Tests for Maintenance Mode middleware and Heroku configuration helpers."""

from app import app


def test_maintenance_mode_blocks_pages_with_503_and_retry_after(monkeypatch):
    monkeypatch.setenv("MAINTENANCE_MODE", "true")
    monkeypatch.delenv("MAINTENANCE_MESSAGE", raising=False)
    monkeypatch.delenv("MAINTENANCE_ETA", raising=False)

    client = app.test_client()
    resp = client.get("/")

    assert resp.status_code == 503
    assert resp.headers.get("Retry-After") == "300"
    html = resp.get_data(as_text=True)
    assert "upgrading our servers" in html.lower()
    assert "AI JobSnap is migrating to faster, always-on servers." in html


def test_maintenance_mode_custom_message_and_eta(monkeypatch):
    monkeypatch.setenv("MAINTENANCE_MODE", "true")
    monkeypatch.setenv("MAINTENANCE_MESSAGE", "Migrating PostgreSQL database to Heroku.")
    monkeypatch.setenv("MAINTENANCE_ETA", "10 minutes")

    client = app.test_client()
    resp = client.get("/login")

    assert resp.status_code == 503
    html = resp.get_data(as_text=True)
    assert "Migrating PostgreSQL database to Heroku." in html
    assert "10 minutes" in html


def test_maintenance_mode_returns_json_for_api_requests(monkeypatch):
    monkeypatch.setenv("MAINTENANCE_MODE", "1")
    monkeypatch.setenv("MAINTENANCE_ETA", "15 minutes")

    client = app.test_client()
    resp = client.get("/api/nonexistent")

    assert resp.status_code == 503
    assert resp.headers.get("Retry-After") == "300"
    payload = resp.get_json()
    assert payload["maintenance"] is True
    assert payload["eta"] == "15 minutes"


def test_maintenance_mode_allows_health_probes(monkeypatch):
    monkeypatch.setenv("MAINTENANCE_MODE", "true")

    client = app.test_client()
    assert client.get("/healthz").status_code == 200
    assert client.get("/ping").status_code == 200


def test_maintenance_mode_disabled_allows_normal_requests(monkeypatch):
    monkeypatch.setenv("MAINTENANCE_MODE", "false")

    client = app.test_client()
    assert client.get("/healthz").status_code == 200
    login_resp = client.get("/login")
    assert login_resp.status_code != 503


def test_postgres_cursor_uses_user_id_returning_for_cooldowns():
    from database import _PostgresCursor

    executed_sql = []

    class _FakeRawCursor:
        description = None
        rowcount = 1

        def execute(self, sql, params=None):
            executed_sql.append(sql)

        def fetchone(self):
            return (7,)

    class _FakeConnection:
        def __init__(self):
            self._raw = self

        def cursor(self, **kwargs):
            return _FakeRawCursor()

        def _next_savepoint(self):
            return "sp_1"

        def _execute_control(self, stmt):
            pass

    cur = _PostgresCursor(_FakeConnection())
    cur.execute(
        "INSERT INTO user_scrape_cooldowns (user_id, completed_count) VALUES (?, ?)",
        (7, 0),
    )
    assert executed_sql[-1].endswith("RETURNING user_id")
    assert cur.lastrowid == 7

