from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


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
        self.auto_delete_days = int(os.getenv("AUTO_DELETE_DAYS", "30"))
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.whisper_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self.piper_binary_path = os.getenv("PIPER_BINARY_PATH", "piper")
        self.piper_voice_path = os.getenv("PIPER_VOICE_PATH", "./data/models/piper/default.onnx")
        self.piper_config_path = os.getenv("PIPER_CONFIG_PATH") or None
        self.max_tts_text_length = int(os.getenv("MAX_TTS_TEXT_LENGTH", "5000"))
        self.login_max_attempts = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
        self.login_lock_seconds = int(os.getenv("LOGIN_LOCK_SECONDS", "300"))
        self.cookie_secure = _bool(os.getenv("COOKIE_SECURE"), self.app_env == "production")

    def ensure_ready(self) -> None:
        if not self.session_secret:
            raise RuntimeError("SESSION_SECRET is required")
        if not self.app_password and not self.app_password_hash:
            raise RuntimeError("APP_PASSWORD or APP_PASSWORD_HASH is required")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
