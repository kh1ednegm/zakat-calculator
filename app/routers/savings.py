from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import SavingsRepository
from app.schemas.finance import SavingIn
from app.security import validate_csrf

router = APIRouter(prefix="/savings", tags=["savings"])

INVALID_MSG = "يرجى التحقق من البيانات: المبلغ يجب أن يكون أكبر من صفر والتاريخ صحيحًا."


def _render_list(request, db, user, *, edit_item=None, error=None, status_code=200):
    items = SavingsRepository(db).list(user.id)
    total = sum((Decimal(i.amount) for i in items), Decimal(0))
    return render(
        request,
        "savings.html",
        {"items": items, "total": total, "edit_item": edit_item, "error": error},
        user=user,
        status_code=status_code,
    )


@router.get("")
def list_savings(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    return _render_list(request, db, user)


@router.post("/add")
def add_saving(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    amount: str = Form(...),
    date_value: str = Form(..., alias="date"),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = SavingIn(amount=amount, date=date_value, description=description.strip() or None)
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    SavingsRepository(db).create(
        user.id, amount=data.amount, date=data.date, description=data.description
    )
    return RedirectResponse("/savings", status_code=303)


@router.get("/{item_id}/edit")
def edit_saving_page(
    item_id: str, request: Request, db: Session = Depends(get_db), user=Depends(require_user)
):
    item = SavingsRepository(db).get(user.id, item_id)
    if item is None:
        return RedirectResponse("/savings", status_code=303)
    return _render_list(request, db, user, edit_item=item)


@router.post("/{item_id}/edit")
def edit_saving(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    amount: str = Form(...),
    date_value: str = Form(..., alias="date"),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = SavingIn(amount=amount, date=date_value, description=description.strip() or None)
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    SavingsRepository(db).update(
        user.id, item_id, amount=data.amount, date=data.date, description=data.description
    )
    return RedirectResponse("/savings", status_code=303)


@router.post("/{item_id}/delete")
def delete_saving(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
):
    validate_csrf(request, csrf_token)
    SavingsRepository(db).delete(user.id, item_id)
    return RedirectResponse("/savings", status_code=303)
