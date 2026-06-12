from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import SettingsRepository
from app.schemas.finance import SettingsIn
from app.security import validate_csrf
from app.services.settings_service import needs_setup

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("")
def onboarding_page(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    user_settings = SettingsRepository(db).get_or_create(user.id)
    if not needs_setup(user_settings):
        return RedirectResponse("/dashboard", status_code=303)
    return render(request, "onboarding.html", {"s": user_settings}, user=user)


@router.post("")
def complete_onboarding(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    gold_price_per_gram: str = Form(...),
    currency: str = Form("ج.م"),
    zakat_date: str = Form(""),
    preferred_method: int = Form(1),
):
    validate_csrf(request, csrf_token)
    repo = SettingsRepository(db)
    try:
        data = SettingsIn(
            gold_price_per_gram=gold_price_per_gram,
            currency=currency.strip() or "ج.م",
            zakat_date=zakat_date or None,
            preferred_method=preferred_method,
        )
    except ValidationError:
        user_settings = repo.get_or_create(user.id)
        return render(
            request,
            "onboarding.html",
            {
                "s": user_settings,
                "error": "يرجى التحقق من البيانات: سعر الذهب مطلوب ويجب أن يكون أكبر من صفر",
            },
            user=user,
            status_code=400,
        )

    if data.preferred_method == 2 and data.zakat_date is None:
        user_settings = repo.get_or_create(user.id)
        return render(
            request,
            "onboarding.html",
            {
                "s": user_settings,
                "error": "عند اختيار «موعد زكاة موحد» يجب تحديد تاريخ الزكاة السنوي",
            },
            user=user,
            status_code=400,
        )

    if data.gold_price_per_gram <= 0:
        user_settings = repo.get_or_create(user.id)
        return render(
            request,
            "onboarding.html",
            {
                "s": user_settings,
                "error": "يرجى إدخال سعر جرام الذهب الحالي (أكبر من صفر)",
            },
            user=user,
            status_code=400,
        )

    repo.update(
        user.id,
        gold_price_per_gram=data.gold_price_per_gram,
        currency=data.currency,
        zakat_date=data.zakat_date,
        preferred_method=data.preferred_method,
    )
    return RedirectResponse("/dashboard?setup=done", status_code=303)
