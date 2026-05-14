from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.auth.session import SESSION_COOKIE, is_valid_session
from app.config import Settings, get_settings


def is_authenticated(request: Request, settings: Settings = Depends(get_settings)) -> bool:
    return is_valid_session(request.cookies.get(SESSION_COOKIE), settings.session_secret or "")


def require_auth(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if not is_authenticated(request, settings):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


def require_page_auth(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if not is_authenticated(request, settings):
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})


def redirect_if_authenticated(request: Request, settings: Settings = Depends(get_settings)):
    if is_authenticated(request, settings):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return None
