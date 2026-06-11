from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps import render, require_user
from app.repositories import GoldRepository, SettingsRepository
from app.schemas.finance import GoldIn
from app.security import validate_csrf
from app.services.zakat_service import gold_value

router = APIRouter(prefix="/gold", tags=["gold"])

INVALID_MSG = "يرجى التحقق من البيانات: الوزن أكبر من صفر، والعيار بين 1 و24، والتاريخ صحيح."


def _render_list(request, db, user, *, edit_item=None, error=None, status_code=200):
    items = GoldRepository(db).list(user.id)
    user_settings = SettingsRepository(db).get_or_create(user.id)
    price = user_settings.gold_price_per_gram or Decimal("0")
    values = {item.id: gold_value(item.weight_grams, item.karat, price) for item in items}
    total = sum(values.values(), Decimal(0))
    return render(
        request,
        "gold.html",
        {
            "items": items,
            "values": values,
            "total": total,
            "gold_price": price,
            "settings": user_settings,
            "edit_item": edit_item,
            "error": error,
        },
        user=user,
        status_code=status_code,
    )


@router.get("")
def list_gold(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    return _render_list(request, db, user)


@router.post("/add")
def add_gold(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    weight_grams: str = Form(...),
    karat: str = Form(...),
    purchase_date: str = Form(...),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = GoldIn(
            weight_grams=weight_grams,
            karat=karat,
            purchase_date=purchase_date,
            description=description.strip() or None,
        )
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    GoldRepository(db).create(
        user.id,
        weight_grams=data.weight_grams,
        karat=data.karat,
        purchase_date=data.purchase_date,
        description=data.description,
    )
    return RedirectResponse("/gold", status_code=303)


@router.get("/{item_id}/edit")
def edit_gold_page(
    item_id: str, request: Request, db: Session = Depends(get_db), user=Depends(require_user)
):
    item = GoldRepository(db).get(user.id, item_id)
    if item is None:
        return RedirectResponse("/gold", status_code=303)
    return _render_list(request, db, user, edit_item=item)


@router.post("/{item_id}/edit")
def edit_gold(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
    weight_grams: str = Form(...),
    karat: str = Form(...),
    purchase_date: str = Form(...),
    description: str = Form(""),
):
    validate_csrf(request, csrf_token)
    try:
        data = GoldIn(
            weight_grams=weight_grams,
            karat=karat,
            purchase_date=purchase_date,
            description=description.strip() or None,
        )
    except ValidationError:
        return _render_list(request, db, user, error=INVALID_MSG, status_code=400)
    GoldRepository(db).update(
        user.id,
        item_id,
        weight_grams=data.weight_grams,
        karat=data.karat,
        purchase_date=data.purchase_date,
        description=data.description,
    )
    return RedirectResponse("/gold", status_code=303)


@router.post("/{item_id}/delete")
def delete_gold(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    csrf_token: str = Form(...),
):
    validate_csrf(request, csrf_token)
    GoldRepository(db).delete(user.id, item_id)
    return RedirectResponse("/gold", status_code=303)
