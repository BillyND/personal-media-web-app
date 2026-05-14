from fastapi.testclient import TestClient

from app.auth.session import SESSION_COOKIE
from app.config import get_settings


def make_client(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD", "secret")
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
    get_settings.cache_clear()
    from app.main import create_app

    return TestClient(create_app())


def test_login_success_sets_session_cookie(monkeypatch, tmp_path):
    client = make_client(monkeypatch, tmp_path)
    response = client.post("/login", data={"password": "secret"}, follow_redirects=False)
    assert response.status_code == 303
    assert SESSION_COOKIE in response.cookies


def test_login_failure_denied(monkeypatch, tmp_path):
    client = make_client(monkeypatch, tmp_path)
    response = client.post("/login", data={"password": "wrong"})
    assert response.status_code == 401


def test_dashboard_requires_auth(monkeypatch, tmp_path):
    client = make_client(monkeypatch, tmp_path)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
