from itsdangerous import BadSignature, URLSafeSerializer
from starlette.responses import Response

SESSION_COOKIE = "media_session"
SESSION_VALUE = "authenticated"


def _serializer(secret: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret_key=secret, salt="media-session")


def create_session_token(secret: str) -> str:
    return _serializer(secret).dumps({"auth": SESSION_VALUE})


def is_valid_session(token: str | None, secret: str) -> bool:
    if not token:
        return False
    try:
        payload = _serializer(secret).loads(token)
    except BadSignature:
        return False
    return payload.get("auth") == SESSION_VALUE


def set_session_cookie(response: Response, token: str, secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)
