import signal
import time

from app.config import get_settings
from app.db.schema import init_db
from app.jobs.processors import process_job
from app.jobs.repository import JobRepository

_SHOULD_STOP = False


def _stop(_signum, _frame) -> None:
    global _SHOULD_STOP
    _SHOULD_STOP = True


def run_worker(poll_seconds: float = 3.0) -> None:
    settings = get_settings()
    settings.ensure_ready()
    init_db()
    repository = JobRepository(settings)
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    while not _SHOULD_STOP:
        job = repository.claim_next_pending()
        if job is None:
            time.sleep(poll_seconds)
            continue
        try:
            process_job(job, repository, settings)
        except Exception as error:
            repository.mark_failed(job.id, str(error))
        else:
            repository.mark_done(job.id)


if __name__ == "__main__":
    run_worker()
