import hashlib

import pytest

from app.config import Settings


def test_config_requires_session_secret(monkeypatch):
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()
    with pytest.raises(RuntimeError):
        settings.ensure_ready()


def test_production_rejects_placeholder_secrets(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_PASSWORD", "change-me")
    monkeypatch.setenv("SESSION_SECRET", "change-me-to-a-long-random-secret")
    settings = Settings()
    with pytest.raises(RuntimeError):
        settings.ensure_ready()


def test_production_rejects_placeholder_password_hash(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    monkeypatch.setenv("APP_PASSWORD_HASH", hashlib.sha256(b"secret").hexdigest())
    monkeypatch.setenv("SESSION_SECRET", "x" * 40)
    settings = Settings()
    with pytest.raises(RuntimeError):
        settings.ensure_ready()


def test_production_rejects_malformed_password_hash(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    monkeypatch.setenv("APP_PASSWORD_HASH", "not-a-sha256")
    monkeypatch.setenv("SESSION_SECRET", "x" * 40)
    settings = Settings()
    with pytest.raises(RuntimeError):
        settings.ensure_ready()
