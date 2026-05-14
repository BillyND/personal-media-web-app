import hashlib
import hmac

from app.config import Settings


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(candidate: str, settings: Settings) -> bool:
    if settings.app_password_hash:
        return hmac.compare_digest(_hash_password(candidate), settings.app_password_hash)
    if not settings.app_password:
        return False
    return hmac.compare_digest(candidate, settings.app_password)
