from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.password import verify_password
from app.auth.rate_limit import LoginRateLimiter
from app.auth.session import clear_session_cookie, create_session_token, set_session_cookie
from app.config import Settings, get_settings
from app.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
_limiter: LoginRateLimiter | None = None


def get_limiter(settings: Settings = Depends(get_settings)) -> LoginRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = LoginRateLimiter(settings.login_max_attempts, settings.login_lock_seconds)
    return _limiter


@router.get("/login")
def login_page(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
def login(
    request: Request,
    password: str = Form(""),
    settings: Settings = Depends(get_settings),
    limiter: LoginRateLimiter = Depends(get_limiter),
):
    client_key = request.client.host if request.client else "unknown"
    if limiter.is_locked(client_key) or not verify_password(password, settings):
        limiter.record_failure(client_key)
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Password không đúng hoặc đang bị tạm khoá."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    limiter.record_success(client_key)
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(response, create_session_token(settings.session_secret or ""), settings.cookie_secure)
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_session_cookie(response)
    return response
