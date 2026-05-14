import sqlite3
from pathlib import Path

from app.config import Settings, get_settings


def get_connection(settings: Settings | None = None) -> sqlite3.Connection:
    settings = settings or get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def resolve_safe_path(base_dir: Path, candidate: str) -> Path:
    path = Path(candidate).resolve()
    if base_dir.resolve() not in path.parents and path != base_dir.resolve():
        raise ValueError("Path is outside allowed directory")
    return path
