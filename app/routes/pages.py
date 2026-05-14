from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import require_page_auth
from app.config import Settings, get_settings
from app.jobs.repository import JobRepository
from app.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", dependencies=[Depends(require_page_auth)])
def dashboard(
    request: Request,
    page: int = Query(1, ge=1),
    settings: Settings = Depends(get_settings),
):
    repository = JobRepository(settings)
    page_size = 10
    total_jobs = repository.count_jobs()
    total_pages = max(1, ceil(total_jobs / page_size))
    current_page = min(page, total_pages)
    jobs = repository.list_jobs(limit=page_size, offset=(current_page - 1) * page_size)
    files_by_job = {job.id: repository.list_files(job.id) for job in jobs}
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "jobs": jobs,
            "files_by_job": files_by_job,
            "page": current_page,
            "total_pages": total_pages,
            "page_size": page_size,
            "total_jobs": total_jobs,
            "tts_languages": settings.tts_languages,
            "tts_voices": settings.tts_voices,
            "default_tts_language_id": settings.default_tts_language_id,
            "default_tts_voice_id": settings.default_tts_voice_id,
        },
    )
