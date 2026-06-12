from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.config import settings
from app.database.session import SessionLocal
from app.deps import RequiresLoginError
from app.repositories import SettingsRepository
from app.routers import (
    auth,
    dashboard,
    debts,
    gold,
    home,
    onboarding,
    reports,
    savings,
    user_settings,
    withdrawals,
    zakat,
)

app = FastAPI(title=settings.APP_NAME, docs_url=None, redoc_url=None)

# Define the custom middleware as a class
class AttachUserSettingsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        """Load user settings once per request so templates can show setup status."""
        request.state.user_settings = None
        
        # --- TEMPORARY DIAGNOSTIC PRINT STATEMENT ---
        print(f"DEBUG: 'session' in request.scope: {'session' in request.scope}")
        # --- END TEMPORARY DIAGNOSTIC PRINT STATEMENT ---

        user_id = request.session.get("user_id")
        if user_id:
            db = SessionLocal()
            try:
                request.state.user_settings = SettingsRepository(db).get_or_create(user_id)
            finally:
                db.close()
        response = await call_next(request)
        return response

# Add AttachUserSettingsMiddleware first (this will be the innermost middleware, executed last)
app.add_middleware(
    AttachUserSettingsMiddleware
)

# Add an explicit check for SECRET_KEY
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY is not set or is empty. Please set it in your .env file.")

# Add SessionMiddleware second (this will be the outermost middleware, executed first)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=settings.ENV == "production",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(RequiresLoginError)
async def requires_login_handler(request: Request, exc: RequiresLoginError):
    return RedirectResponse(url="/login", status_code=303)


for router in (
    home.router,
    auth.router,
    onboarding.router,
    dashboard.router,
    savings.router,
    gold.router,
    debts.router,
    withdrawals.router,
    zakat.router,
    reports.router,
    user_settings.router,
):
    app.include_router(router)