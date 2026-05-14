from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.connection import resolve_safe_path
from app.db.schema import init_db
from app.jobs.models import JOB_TTS
from app.jobs.repository import JobRepository
from app.main import create_app


def make_client(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_PASSWORD", "secret")
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
    get_settings.cache_clear()
    return TestClient(create_app())


def login(client):
    client.post("/login", data={"password": "secret"}, follow_redirects=False)


def test_resolve_safe_path_rejects_traversal(tmp_path):
    outside = Path(tmp_path).parent / "outside.txt"
    with pytest.raises(ValueError):
        resolve_safe_path(tmp_path, str(outside))


def test_preview_text_file_after_login(tmp_path, monkeypatch):
    client = make_client(monkeypatch, tmp_path)
    login(client)
    settings = get_settings()
    init_db()
    repository = JobRepository(settings)
    job = repository.create_job(JOB_TTS, input_text="hello")
    transcript = Path(job.output_dir) / "transcript.txt"
    transcript.write_text("hello world", encoding="utf-8")
    job_file = repository.add_file(job.id, "transcript", transcript)

    response = client.get(f"/files/{job_file.id}/preview")
    assert response.status_code == 200
    assert response.text == "hello world"
    assert response.headers["content-type"].startswith("text/plain")


def test_preview_requires_auth(tmp_path, monkeypatch):
    client = make_client(monkeypatch, tmp_path)
    response = client.get("/files/missing/preview")
    assert response.status_code == 401
