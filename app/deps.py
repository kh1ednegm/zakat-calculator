from decimal import Decimal, InvalidOperation

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models import User
from app.security import get_csrf_token

templates = Jinja2Templates(directory="app/templates")


def _money(value) -> str:
    try:
        return f"{Decimal(value):,.2f}"
    except (InvalidOperation, TypeError, ValueError):
        return str(value)


templates.env.filters["money"] = _money


class RequiresLoginError(Exception):
    """Raised when an anonymous user tries to access a protected page."""


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise RequiresLoginError()
    return user


def render(request: Request, template: str, context: dict | None = None, *, user=None, status_code: int = 200):
    ctx = {
        "request": request,
        "user": user,
        "csrf_token": get_csrf_token(request),
        "app_name": settings.APP_NAME,
    }
    if context:
        ctx.update(context)
    return templates.TemplateResponse(template, ctx, status_code=status_code)
