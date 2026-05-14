import json
from pathlib import Path

import pytest

from app.config import Settings
from app.jobs.models import Job
from app.jobs.processors import parse_tts_payload, process_tts_job, strip_tts_symbols
from app.media.vieneu_tts import find_preset_id, normalize_text, synthesize_with_vieneu


class DummyVoice:
    id = "en_US-ryan-medium"
    label = "English · Ryan"
    language = "English"
    language_id = "en"
    engine = "piper"
    model_path = "voice.onnx"
    config_path = None


class DummyVieneuVoice:
    id = "vieneu:tuyen"
    label = "Tuyên · nam Bắc"
    language = "Tiếng Việt"
    language_id = "vi"
    engine = "vieneu"
    model_path = None
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
    vieneu_emotion = "natural"

    def get_tts_voice(self, voice_id, language_id=None):
        if voice_id == DummyVieneuVoice.id:
            return DummyVieneuVoice()
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


def test_process_tts_uses_vieneu_for_vieneu_voice(tmp_path, monkeypatch):
    calls = []

    def fake_synthesize(text, output_wav, voice_id, settings):
        calls.append((text, voice_id))
        Path(output_wav).write_bytes(b"wav")

    def fake_convert(input_wav, output_mp3, timeout_seconds):
        Path(output_mp3).write_bytes(b"mp3")

    monkeypatch.setattr("app.jobs.processors.synthesize_with_vieneu", fake_synthesize)
    monkeypatch.setattr("app.jobs.processors.convert_wav_to_mp3", fake_convert)
    payload = json.dumps({"text": "xin chào 🔥", "voice_id": "vieneu:tuyen"})
    job = Job("1", "tts", "pending", None, payload, str(tmp_path), None, "now", None, None)
    repository = DummyRepository()

    settings = DummySettings()
    settings.max_tts_text_length = 100

    process_tts_job(job, repository, settings)

    assert calls == [("xin chào", "vieneu:tuyen")]
    assert (tmp_path / "metadata.json").read_text(encoding="utf-8").find('"engine": "vieneu"') > -1


def test_find_vieneu_preset_id_matches_vietnamese_names():
    voices = [("Bác sĩ Tuyên - Male North", "voice_tuyen"), ("Anh Bình", "voice_binh")]
    assert find_preset_id(voices, "vieneu:tuyen") == "voice_tuyen"
    assert find_preset_id(voices, "vieneu:binh") == "voice_binh"


def test_normalize_text_removes_vietnamese_accents():
    assert normalize_text("Tuyên Nguyễn") == "tuyen nguyen"


def test_vieneu_missing_dependency_has_clear_error(tmp_path, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "vieneu":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="runtime/bin/python -m pip install vieneu"):
        synthesize_with_vieneu("xin chào", tmp_path / "audio.wav", "vieneu:tuyen", DummySettings())


def test_settings_include_vietnamese_tts_voice(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()

    voice = settings.get_tts_voice("vi_VN-vais1000-medium", "vi")

    assert voice.language == "Tiếng Việt"
    assert voice.model_path.endswith("vi_VN-vais1000-medium.onnx")


def test_settings_include_vieneu_male_voices(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()

    voice_ids = {voice.id for voice in settings.tts_voices if voice.engine == "vieneu"}

    assert {"vieneu:binh", "vieneu:tuyen", "vieneu:nguyen"}.issubset(voice_ids)
    assert settings.get_tts_voice("vieneu:tuyen", "vi").engine == "vieneu"


def test_settings_reject_voice_language_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setenv("APP_PASSWORD", "secret")
    settings = Settings()

    with pytest.raises(ValueError):
        settings.get_tts_voice("en_US-ryan-medium", "vi")
