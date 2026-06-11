from decimal import Decimal

from fastapi import APIRouter, Depends, Request, Response
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
from app.services.pdf_service import generate_report
from app.services.zakat_service import calculate_method1, calculate_method2

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def reports_page(request: Request, user=Depends(require_user)):
    return render(request, "reports.html", user=user)


@router.get("/pdf")
def reports_pdf(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    user_settings = SettingsRepository(db).get_or_create(user.id)
    savings = SavingsRepository(db).list(user.id)
    gold_items = GoldRepository(db).list(user.id)
    debts = DebtRepository(db).list(user.id)
    withdrawals = WithdrawalRepository(db).list(user.id)

    price = user_settings.gold_price_per_gram or Decimal("0")
    m1 = calculate_method1(savings, gold_items, debts, withdrawals, price)
    m2 = calculate_method2(
        savings, gold_items, debts, withdrawals, price, zakat_date=user_settings.zakat_date
    )
    pdf_bytes = generate_report(
        user=user,
        user_settings=user_settings,
        savings=savings,
        gold_assets=gold_items,
        debts=debts,
        withdrawals=withdrawals,
        m1=m1,
        m2=m2,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="zakat-report.pdf"'},
    )
