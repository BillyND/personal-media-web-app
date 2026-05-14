from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth.dependencies import require_auth
from app.config import Settings, get_settings
from app.db.connection import resolve_safe_path
from app.jobs.repository import JobRepository

router = APIRouter()


@router.get("/files/{file_id}", dependencies=[Depends(require_auth)])
def download_file(file_id: str, settings: Settings = Depends(get_settings)):
    try:
        job_file = JobRepository(settings).get_file(file_id)
        path = resolve_safe_path(settings.output_dir, job_file.path)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="File not found") from None
    if not Path(path).is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=Path(path).name)
