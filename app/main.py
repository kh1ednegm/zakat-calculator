from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.deps import RequiresLoginError
from app.routers import (
    auth,
    dashboard,
    debts,
    gold,
    home,
    reports,
    savings,
    user_settings,
    withdrawals,
    zakat,
)

app = FastAPI(title=settings.APP_NAME, docs_url=None, redoc_url=None)

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
