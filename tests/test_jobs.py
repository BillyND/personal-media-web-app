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
