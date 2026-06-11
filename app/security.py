import secrets

from fastapi import HTTPException, Request
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password, password_hash)
    except ValueError:
        return False


def get_csrf_token(request: Request) -> str:
    """Return the session CSRF token, generating one if needed."""
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_hex(32)
        request.session["csrf_token"] = token
    return token


def validate_csrf(request: Request, token: str | None) -> None:
    """Validate the submitted CSRF token against the session token."""
    expected = request.session.get("csrf_token")
    if not token or not expected or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=403, detail="فشل التحقق من الأمان (CSRF)")
