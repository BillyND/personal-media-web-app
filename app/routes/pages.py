from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import require_page_auth
from app.config import Settings, get_settings
from app.jobs.repository import JobRepository
from app.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", dependencies=[Depends(require_page_auth)])
def dashboard(request: Request, settings: Settings = Depends(get_settings)):
    repository = JobRepository(settings)
    jobs = repository.list_jobs()
    files_by_job = {job.id: repository.list_files(job.id) for job in jobs}
    return templates.TemplateResponse(
        request, "dashboard.html", {"jobs": jobs, "files_by_job": files_by_job}
    )
