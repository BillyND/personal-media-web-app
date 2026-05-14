import logging
import signal
import time

from app.config import get_settings
from app.db.schema import init_db
from app.jobs.processors import process_job
from app.jobs.repository import JobRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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
    logger.info("Worker started; polling for pending jobs every %.1fs", poll_seconds)

    while not _SHOULD_STOP:
        stale_count = repository.fail_stale_processing(settings.job_stale_minutes)
        if stale_count:
            logger.warning("Marked %s stale processing job(s) as failed", stale_count)
        job = repository.claim_next_pending()
        if job is None:
            time.sleep(poll_seconds)
            continue
        logger.info("Claimed job %s type=%s", job.id, job.type)
        try:
            process_job(job, repository, settings)
        except Exception as error:
            repository.mark_failed(job.id, str(error))
            logger.exception("Job %s failed: %s", job.id, error)
        else:
            repository.mark_done(job.id)
            logger.info("Job %s completed", job.id)
    logger.info("Worker stopped")


if __name__ == "__main__":
    run_worker()
