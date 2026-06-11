from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import DebtRepository
from app.schemas.finance import DebtIn
from app.security import validate_csrf

router = APIRouter(prefix="/debts", tags=["debts"])

INVALID_MSG = "يرجى التحقق من البيانات: المبلغ يجب أن يكون أكبر من صفر والتاريخ صحيحًا."


def _render_list(request, db, user, *, edit_item=None, error=None, status_code=200):
    items = DebtRepository(db).list(user.id)
    total = sum((Decimal(i.amount) for i in items), Decimal(0))
    return render(
        request,
        "debts.html",
        {"items": items, "total": total, "edit_item": edit_item, "error": error},
        user=user,
        status_code=status_code,
    )


@router.get("")
def list_debts(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    return _render_list(request, db, user)


@router.post("/add")
def add_debt(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    amount: str = Form(...),
    due_date: str = Form(...),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = DebtIn(amount=amount, due_date=due_date, description=description.strip() or None)
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    DebtRepository(db).create(
        user.id, amount=data.amount, due_date=data.due_date, description=data.description
    )
    return RedirectResponse("/debts", status_code=303)


@router.get("/{item_id}/edit")
def edit_debt_page(
    item_id: str, request: Request, db: Session = Depends(get_db), user=Depends(require_user)
):
    item = DebtRepository(db).get(user.id, item_id)
    if item is None:
        return RedirectResponse("/debts", status_code=303)
    return _render_list(request, db, user, edit_item=item)


@router.post("/{item_id}/edit")
def edit_debt(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    amount: str = Form(...),
    due_date: str = Form(...),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = DebtIn(amount=amount, due_date=due_date, description=description.strip() or None)
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    DebtRepository(db).update(
        user.id, item_id, amount=data.amount, due_date=data.due_date, description=data.description
    )
    return RedirectResponse("/debts", status_code=303)


@router.post("/{item_id}/delete")
def delete_debt(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
):
    validate_csrf(request, csrf_token)
    DebtRepository(db).delete(user.id, item_id)
    return RedirectResponse("/debts", status_code=303)
