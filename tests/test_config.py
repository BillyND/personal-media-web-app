import pytest

from app.config import Settings


def test_config_requires_session_secret(monkeypatch):
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()
    with pytest.raises(RuntimeError):
        settings.ensure_ready()
