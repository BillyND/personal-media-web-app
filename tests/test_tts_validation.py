import json
from pathlib import Path

import pytest

from app.config import Settings
from app.jobs.models import Job
from app.jobs.processors import parse_tts_payload, process_tts_job, strip_tts_symbols


class DummyVoice:
    id = "en_US-ryan-medium"
    label = "English · Ryan"
    language = "English"
    language_id = "en"
    model_path = "voice.onnx"
    config_path = None


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
    command_timeout_seconds = 300

    def get_tts_voice(self, voice_id, language_id=None):
        if voice_id and voice_id != DummyVoice.id:
            raise ValueError("Unsupported TTS voice")
        if language_id and language_id != DummyVoice.language_id:
            raise ValueError("TTS voice does not match selected language")
        return DummyVoice()


def test_tts_rejects_oversized_text(tmp_path):
    job = Job("1", "tts", "pending", None, "hello", str(tmp_path), None, "now", None, None)
    with pytest.raises(ValueError):
        process_tts_job(job, DummyRepository(), DummySettings())


def test_tts_rejects_unknown_voice(tmp_path):
    payload = json.dumps({"text": "hi", "voice_id": "missing"})
    job = Job("1", "tts", "pending", None, payload, str(tmp_path), None, "now", None, None)
    with pytest.raises(ValueError):
        process_tts_job(job, DummyRepository(), DummySettings())


def test_parse_tts_payload_supports_legacy_plain_text():
    assert parse_tts_payload("hello") == ("hello", None)


def test_parse_tts_payload_supports_json_voice():
    assert parse_tts_payload('{"text":"hello","voice_id":"en_US-ryan-medium"}') == (
        "hello",
        "en_US-ryan-medium",
    )


def test_strip_tts_symbols_removes_icons_and_emoji():
    assert strip_tts_symbols("Hello 🔥 world ✅ #1") == "Hello world #1"


def test_settings_include_vietnamese_tts_voice(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()

    voice = settings.get_tts_voice("vi_VN-vais1000-medium", "vi")

    assert voice.language == "Tiếng Việt"
    assert voice.model_path.endswith("vi_VN-vais1000-medium.onnx")


def test_settings_reject_voice_language_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()

    with pytest.raises(ValueError):
        settings.get_tts_voice("en_US-ryan-medium", "vi")
