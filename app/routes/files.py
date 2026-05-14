from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.auth.dependencies import require_auth
from app.config import Settings, get_settings
from app.db.connection import resolve_safe_path
from app.jobs.models import JobFile
from app.jobs.repository import JobRepository

router = APIRouter()

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
TEXT_EXTENSIONS = {".txt", ".json"}


@router.get("/files/{file_id}", dependencies=[Depends(require_auth)])
def download_file(file_id: str, settings: Settings = Depends(get_settings)):
    job_file, path = get_safe_file(file_id, settings)
    return FileResponse(path, filename=Path(path).name, media_type=media_type_for(job_file, path))


@router.get("/files/{file_id}/preview", dependencies=[Depends(require_auth)])
def preview_file(file_id: str, settings: Settings = Depends(get_settings)):
    job_file, path = get_safe_file(file_id, settings)
    suffix = Path(path).suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        text = read_preview_text(path, settings.max_preview_bytes)
        return PlainTextResponse(text, media_type=media_type_for(job_file, path))
    if suffix in AUDIO_EXTENSIONS or suffix in VIDEO_EXTENSIONS:
        return FileResponse(path, media_type=media_type_for(job_file, path))
    raise HTTPException(status_code=415, detail="Preview is not supported for this file")


def get_safe_file(file_id: str, settings: Settings) -> tuple[JobFile, Path]:
    try:
        job_file = JobRepository(settings).get_file(file_id)
        path = resolve_safe_path(settings.output_dir, job_file.path)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="File not found") from None
    if not Path(path).is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return job_file, path


def read_preview_text(path: Path, max_bytes: int) -> str:
    data = path.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="replace")
    if path.stat().st_size > max_bytes:
        text += "\n\n[Preview truncated]"
    return text


def media_type_for(job_file: JobFile, path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".mp3":
        return "audio/mpeg"
    if suffix == ".wav":
        return "audio/wav"
    if suffix == ".m4a":
        return "audio/mp4"
    if suffix == ".mp4":
        return "video/mp4"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mov":
        return "video/quicktime"
    if suffix == ".json":
        return "application/json"
    if suffix == ".txt" or job_file.kind in {"transcript", "input"}:
        return "text/plain; charset=utf-8"
    return "application/octet-stream"
