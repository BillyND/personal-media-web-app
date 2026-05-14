from dataclasses import dataclass
from sqlite3 import Row

JOB_PENDING = "pending"
JOB_PROCESSING = "processing"
JOB_DONE = "done"
JOB_FAILED = "failed"
JOB_TIKTOK = "tiktok"
JOB_TTS = "tts"


@dataclass(frozen=True)
class Job:
    id: str
    type: str
    status: str
    input_url: str | None
    input_text: str | None
    output_dir: str
    error_message: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None

    @classmethod
    def from_row(cls, row: Row) -> "Job":
        return cls(**dict(row))


@dataclass(frozen=True)
class JobFile:
    id: str
    job_id: str
    kind: str
    path: str
    created_at: str

    @classmethod
    def from_row(cls, row: Row) -> "JobFile":
        return cls(**dict(row))
