from datetime import UTC, datetime, timedelta

from app.db.connection import get_connection
from app.db.schema import init_db
from app.jobs.models import JOB_PENDING, JOB_PROCESSING, JOB_TTS
from app.jobs.repository import JobRepository


def test_job_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("APP_PASSWORD", "secret")
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    from app.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    settings.ensure_ready()
    init_db()
    repository = JobRepository(settings)

    job = repository.create_job(JOB_TTS, input_text="hello")
    assert job.status == JOB_PENDING

    claimed = repository.claim_next_pending()
    assert claimed is not None
    assert claimed.status == JOB_PROCESSING

    repository.mark_failed(claimed.id, "boom")
    failed = repository.get_job(claimed.id)
    assert failed.status == "failed"
    assert failed.error_message == "boom"


def test_stale_processing_jobs_are_failed(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("APP_PASSWORD", "secret")
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    from app.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    settings.ensure_ready()
    init_db()
    repository = JobRepository(settings)
    job = repository.create_job(JOB_TTS, input_text="hello")
    claimed = repository.claim_next_pending()
    old_started_at = (datetime.now(UTC) - timedelta(minutes=10)).isoformat()
    with get_connection(settings) as connection:
        connection.execute("update jobs set started_at = ? where id = ?", (old_started_at, claimed.id))

    assert repository.fail_stale_processing(5) == 1
    assert repository.get_job(job.id).status == "failed"
