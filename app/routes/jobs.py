from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import require_auth, require_page_auth
from app.config import Settings, get_settings
from app.jobs.models import JOB_TIKTOK, JOB_TTS
from app.jobs.repository import JobRepository
from app.media.tiktok_downloader import validate_tiktok_url
from app.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.post("/jobs/tiktok", dependencies=[Depends(require_auth)])
def create_tiktok_job(url: str = Form(""), settings: Settings = Depends(get_settings)):
    try:
        clean_url = validate_tiktok_url(url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
    JobRepository(settings).create_job(JOB_TIKTOK, input_url=clean_url)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/jobs/tts", dependencies=[Depends(require_auth)])
def create_tts_job(text: str = Form(""), settings: Settings = Depends(get_settings)):
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if len(text) > settings.max_tts_text_length:
        raise HTTPException(status_code=400, detail="Text exceeds configured length limit")
    JobRepository(settings).create_job(JOB_TTS, input_text=text)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/jobs", dependencies=[Depends(require_page_auth)])
def jobs_fragment(request: Request, settings: Settings = Depends(get_settings)):
    repository = JobRepository(settings)
    jobs = repository.list_jobs()
    files_by_job = {job.id: repository.list_files(job.id) for job in jobs}
    return templates.TemplateResponse(
        request, "partials/jobs-table.html", {"jobs": jobs, "files_by_job": files_by_job}
    )


@router.get("/jobs/{job_id}", dependencies=[Depends(require_page_auth)])
def job_detail(job_id: str, request: Request, settings: Settings = Depends(get_settings)):
    repository = JobRepository(settings)
    job = repository.get_job(job_id)
    files = repository.list_files(job_id)
    return templates.TemplateResponse(request, "partials/job-detail.html", {"job": job, "files": files})
