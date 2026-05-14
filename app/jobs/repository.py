from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.config import Settings, get_settings
from app.db.connection import get_connection
from app.jobs.models import JOB_FAILED, JOB_PENDING, JOB_PROCESSING, Job, JobFile


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class JobRepository:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def create_job(self, job_type: str, input_url: str | None = None, input_text: str | None = None) -> Job:
        job_id = uuid4().hex
        output_dir = self.settings.output_dir / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        now = utc_now()
        with get_connection(self.settings) as connection:
            connection.execute(
                """
                insert into jobs(id, type, status, input_url, input_text, output_dir, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, job_type, JOB_PENDING, input_url, input_text, str(output_dir), now),
            )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> Job:
        with get_connection(self.settings) as connection:
            row = connection.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return Job.from_row(row)

    def list_jobs(self, limit: int = 50) -> list[Job]:
        with get_connection(self.settings) as connection:
            rows = connection.execute(
                "select * from jobs order by created_at desc limit ?", (limit,)
            ).fetchall()
        return [Job.from_row(row) for row in rows]

    def list_files(self, job_id: str) -> list[JobFile]:
        with get_connection(self.settings) as connection:
            rows = connection.execute(
                "select * from job_files where job_id = ? order by created_at", (job_id,)
            ).fetchall()
        return [JobFile.from_row(row) for row in rows]

    def get_file(self, file_id: str) -> JobFile:
        with get_connection(self.settings) as connection:
            row = connection.execute("select * from job_files where id = ?", (file_id,)).fetchone()
        if row is None:
            raise KeyError(file_id)
        return JobFile.from_row(row)

    def claim_next_pending(self) -> Job | None:
        now = utc_now()
        with get_connection(self.settings) as connection:
            connection.execute("begin immediate")
            row = connection.execute(
                "select * from jobs where status = ? order by created_at limit 1", (JOB_PENDING,)
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            connection.execute(
                "update jobs set status = ?, started_at = ? where id = ?",
                (JOB_PROCESSING, now, row["id"]),
            )
            connection.commit()
        return self.get_job(row["id"])

    def mark_done(self, job_id: str) -> None:
        with get_connection(self.settings) as connection:
            connection.execute(
                "update jobs set status = 'done', completed_at = ?, error_message = null where id = ?",
                (utc_now(), job_id),
            )

    def mark_failed(self, job_id: str, error_message: str) -> None:
        with get_connection(self.settings) as connection:
            connection.execute(
                "update jobs set status = ?, completed_at = ?, error_message = ? where id = ?",
                (JOB_FAILED, utc_now(), error_message[:1000], job_id),
            )

    def add_file(self, job_id: str, kind: str, path: Path) -> JobFile:
        file_id = uuid4().hex
        with get_connection(self.settings) as connection:
            connection.execute(
                "insert into job_files(id, job_id, kind, path, created_at) values (?, ?, ?, ?, ?)",
                (file_id, job_id, kind, str(path), utc_now()),
            )
        return self.get_file(file_id)
