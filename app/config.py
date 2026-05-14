from functools import lru_cache
from pathlib import Path
import hashlib
import os
import string

from dotenv import load_dotenv

load_dotenv()


class TtsVoice:
    def __init__(
        self,
        id: str,
        label: str,
        language: str,
        language_id: str,
        sample_text: str,
        engine: str = "piper",
        model_path: str | None = None,
        config_path: str | None = None,
    ) -> None:
        self.id = id
        self.label = label
        self.language = language
        self.language_id = language_id
        self.sample_text = sample_text
        self.engine = engine
        self.model_path = model_path
        self.config_path = config_path


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _project_path(value: str | None, fallback: Path) -> str:
    path = Path(value) if value else fallback
    if not path.is_absolute():
        path = PROJECT_DIR / path
    return str(path)


UNSAFE_PASSWORD_HASHES = {_sha256(value) for value in {"change-me", "password", "secret"}}
PROJECT_DIR = Path(__file__).resolve().parents[1]


class Settings:
    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_password = os.getenv("APP_PASSWORD")
        self.app_password_hash = os.getenv("APP_PASSWORD_HASH")
        self.session_secret = os.getenv("SESSION_SECRET")
        self.data_dir = Path(os.getenv("DATA_DIR", "./data")).resolve()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", str(self.data_dir / "outputs"))).resolve()
        self.database_path = self.data_dir / "app.db"
        self.max_video_duration_seconds = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "900"))
        self.max_download_bytes = int(os.getenv("MAX_DOWNLOAD_BYTES", "524288000"))
        self.command_timeout_seconds = int(os.getenv("COMMAND_TIMEOUT_SECONDS", "300"))
        self.job_stale_minutes = int(os.getenv("JOB_STALE_MINUTES", "120"))
        self.auto_delete_seconds = int(os.getenv("AUTO_DELETE_SECONDS", os.getenv("AUTO_DELETE_DAYS", "30")))
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.whisper_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self.piper_binary_path = _project_path(
            os.getenv("PIPER_BINARY_PATH"), PROJECT_DIR / "runtime" / "bin" / "piper"
        )
        self.piper_voice_path = _project_path(
            self._voice_path_env("PIPER_VOICE_PATH", "en_US-ryan-medium.onnx"),
            self.data_dir / "models" / "piper" / "en_US-ryan-medium.onnx",
        )
        self.piper_config_path = _project_path(
            self._voice_path_env("PIPER_CONFIG_PATH", "en_US-ryan-medium.onnx.json"),
            self.data_dir / "models" / "piper" / "en_US-ryan-medium.onnx.json",
        )
        self.max_tts_text_length = int(os.getenv("MAX_TTS_TEXT_LENGTH", "5000"))
        self.vieneu_emotion = os.getenv("VIENEU_EMOTION", "natural")
        self.max_preview_bytes = int(os.getenv("MAX_PREVIEW_BYTES", "262144"))
        self.login_max_attempts = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
        self.login_lock_seconds = int(os.getenv("LOGIN_LOCK_SECONDS", "300"))
        self.cookie_secure = _bool(os.getenv("COOKIE_SECURE"), self.app_env == "production")
        self.tts_voices = self._load_tts_voices()
        self.default_tts_voice_id = os.getenv("DEFAULT_TTS_VOICE_ID", self.tts_voices[0].id)
        self.default_tts_language_id = self.get_tts_voice(self.default_tts_voice_id).language_id

    def _voice_path_env(self, key: str, default_name: str) -> str | None:
        value = os.getenv(key)
        if not value:
            return None
        unsafe_name = "default.onnx.json" if default_name.endswith(".json") else "default.onnx"
        return None if Path(value).name == unsafe_name else value

    def _load_tts_voices(self) -> list[TtsVoice]:
        return [
            TtsVoice(
                id="en_US-ryan-medium",
                label="Ryan",
                language="English",
                language_id="en",
                sample_text="Hello, this is a local English voice.",
                model_path=self.piper_voice_path,
                config_path=self.piper_config_path,
            ),
            TtsVoice(
                id="vi_VN-vais1000-medium",
                label="VAIS1000",
                language="Tiếng Việt",
                language_id="vi",
                sample_text="Xin chào, đây là giọng tiếng Việt chạy cục bộ.",
                model_path=_project_path(None, self.data_dir / "models" / "piper" / "vi_VN-vais1000-medium.onnx"),
                config_path=_project_path(None, self.data_dir / "models" / "piper" / "vi_VN-vais1000-medium.onnx.json"),
            ),
            TtsVoice(
                id="vieneu:binh",
                label="Bình · nam Bắc",
                language="Tiếng Việt",
                language_id="vi",
                sample_text="Xin chào, tôi đang đọc bằng giọng nam miền Bắc tự nhiên.",
                engine="vieneu",
            ),
            TtsVoice(
                id="vieneu:tuyen",
                label="Tuyên · nam Bắc",
                language="Tiếng Việt",
                language_id="vi",
                sample_text="Xin chào, tôi đang đọc bằng giọng nam miền Bắc có nhấn nhá.",
                engine="vieneu",
            ),
            TtsVoice(
                id="vieneu:nguyen",
                label="Nguyên · nam Nam",
                language="Tiếng Việt",
                language_id="vi",
                sample_text="Xin chào, tôi đang đọc bằng giọng nam miền Nam tự nhiên.",
                engine="vieneu",
            ),
        ]

    @property
    def tts_languages(self) -> list[dict[str, str]]:
        languages: dict[str, str] = {}
        for voice in self.tts_voices:
            languages.setdefault(voice.language_id, voice.language)
        return [{"id": key, "label": label} for key, label in languages.items()]

    def get_tts_voice(self, voice_id: str | None, language_id: str | None = None) -> TtsVoice:
        selected_id = voice_id or self.default_tts_voice_id
        for voice in self.tts_voices:
            if voice.id == selected_id:
                if language_id and voice.language_id != language_id:
                    raise ValueError("TTS voice does not match selected language")
                return voice
        raise ValueError("Unsupported TTS voice")

    def ensure_ready(self) -> None:
        if not self.session_secret:
            raise RuntimeError("SESSION_SECRET is required")
        if not self.app_password and not self.app_password_hash:
            raise RuntimeError("APP_PASSWORD or APP_PASSWORD_HASH is required")
        if self.app_env == "production":
            if self.session_secret.startswith("change-me") or len(self.session_secret) < 32:
                raise RuntimeError("SESSION_SECRET is unsafe for production")
            if self.app_password in {"change-me", "password", "secret"}:
                raise RuntimeError("APP_PASSWORD is unsafe for production")
            if self.app_password_hash:
                is_sha256 = len(self.app_password_hash) == 64 and all(
                    char in string.hexdigits for char in self.app_password_hash
                )
                if not is_sha256 or self.app_password_hash.lower() in UNSAFE_PASSWORD_HASHES:
                    raise RuntimeError("APP_PASSWORD_HASH is unsafe for production")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
