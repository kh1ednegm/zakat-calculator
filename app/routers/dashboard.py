from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import (
    DebtRepository,
    GoldRepository,
    SavingsRepository,
    SettingsRepository,
    WithdrawalRepository,
)
from app.services.zakat_service import dashboard_summary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard_page(
    request: Request, db: Session = Depends(get_db), user=Depends(require_user)
):
    user_settings = SettingsRepository(db).get_or_create(user.id)
    summary = dashboard_summary(
        SavingsRepository(db).list(user.id),
        GoldRepository(db).list(user.id),
        DebtRepository(db).list(user.id),
        WithdrawalRepository(db).list(user.id),
        user_settings.gold_price_per_gram or Decimal("0"),
        user_settings.zakat_date,
    )
    return render(
        request,
        "dashboard.html",
        {"summary": summary, "settings": user_settings},
        user=user,
    )
