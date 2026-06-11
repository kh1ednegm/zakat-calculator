from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import get_current_user, render
from app.schemas.auth import LoginIn, RegisterIn
from app.security import validate_csrf
from app.services import auth_service

router = APIRouter(tags=["auth"])


@router.get("/register")
def register_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return render(request, "register.html")


@router.post("/register")
def register(
    request: Request,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    validate_csrf(request, csrf_token)
    if password != password_confirm:
        return render(
            request, "register.html", {"error": "كلمتا المرور غير متطابقتين"}, status_code=400
        )
    try:
        data = RegisterIn(
            full_name=full_name.strip(), email=email.strip().lower(), password=password
        )
    except ValidationError:
        return render(
            request,
            "register.html",
            {"error": "يرجى التحقق من البيانات: بريد إلكتروني صحيح وكلمة مرور لا تقل عن 8 أحرف"},
            status_code=400,
        )
    try:
        user = auth_service.register(
            db, email=data.email, full_name=data.full_name, password=data.password
        )
    except ValueError as exc:
        return render(request, "register.html", {"error": str(exc)}, status_code=400)
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/login")
def login_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return render(request, "login.html")


@router.post("/login")
def login(
    request: Request,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    validate_csrf(request, csrf_token)
    try:
        data = LoginIn(email=email.strip().lower(), password=password)
    except ValidationError:
        return render(request, "login.html", {"error": "بيانات الدخول غير صحيحة"}, status_code=400)
    user = auth_service.authenticate(db, email=data.email, password=data.password)
    if user is None:
        return render(request, "login.html", {"error": "بيانات الدخول غير صحيحة"}, status_code=400)
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    validate_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse("/", status_code=303)
