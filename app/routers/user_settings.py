from fastapi import APIRouter, Depends, Form, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import SettingsRepository
from app.schemas.finance import SettingsIn
from app.security import validate_csrf

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def settings_page(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    user_settings = SettingsRepository(db).get_or_create(user.id)
    return render(request, "settings.html", {"s": user_settings}, user=user)


@router.post("")
def update_settings(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    gold_price_per_gram: str = Form(...),
    currency: str = Form("ر.س"),
    zakat_date: str = Form(""),
    preferred_method: int = Form(1),
):
    validate_csrf(request, csrf_token)
    repo = SettingsRepository(db)
    try:
        data = SettingsIn(
            gold_price_per_gram=gold_price_per_gram,
            currency=currency.strip() or "ر.س",
            zakat_date=zakat_date or None,
            preferred_method=preferred_method,
        )
    except ValidationError:
        user_settings = repo.get_or_create(user.id)
        return render(
            request,
            "settings.html",
            {"s": user_settings, "error": "يرجى التحقق من البيانات المدخلة"},
            user=user,
            status_code=400,
        )
    user_settings = repo.update(
        user.id,
        gold_price_per_gram=data.gold_price_per_gram,
        currency=data.currency,
        zakat_date=data.zakat_date,
        preferred_method=data.preferred_method,
    )
    return render(
        request,
        "settings.html",
        {"s": user_settings, "success": "تم حفظ الإعدادات بنجاح"},
        user=user,
    )
