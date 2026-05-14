from pathlib import Path

import pytest

from app.jobs.models import Job
from app.jobs.processors import process_tts_job


class DummyRepository:
    def __init__(self):
        self.files = []

    def add_file(self, job_id, kind, path):
        self.files.append((job_id, kind, path))


class DummySettings:
    max_tts_text_length = 3
    piper_binary_path = "piper"
    piper_voice_path = "voice.onnx"
    piper_config_path = None


def test_tts_rejects_oversized_text(tmp_path):
    job = Job("1", "tts", "pending", None, "hello", str(tmp_path), None, "now", None, None)
    with pytest.raises(ValueError):
        process_tts_job(job, DummyRepository(), DummySettings())
