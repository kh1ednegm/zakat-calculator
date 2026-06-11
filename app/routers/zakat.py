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
from app.services.zakat_service import DISCLAIMER, calculate_method1, calculate_method2

router = APIRouter(tags=["zakat"])


@router.get("/zakat")
def zakat_page(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    user_settings = SettingsRepository(db).get_or_create(user.id)
    savings = SavingsRepository(db).list(user.id)
    gold_items = GoldRepository(db).list(user.id)
    debts = DebtRepository(db).list(user.id)
    withdrawals = WithdrawalRepository(db).list(user.id)

    price = user_settings.gold_price_per_gram or Decimal("0")
    warning = None
    if price <= 0:
        warning = (
            "لم يتم إدخال سعر جرام الذهب بعد. "
            "يرجى تحديثه من صفحة الإعدادات للحصول على نتائج دقيقة."
        )

    m1 = calculate_method1(savings, gold_items, debts, withdrawals, price)
    m2 = calculate_method2(
        savings, gold_items, debts, withdrawals, price, zakat_date=user_settings.zakat_date
    )
    return render(
        request,
        "zakat.html",
        {
            "m1": m1,
            "m2": m2,
            "settings": user_settings,
            "warning": warning,
            "disclaimer": DISCLAIMER,
        },
        user=user,
    )
