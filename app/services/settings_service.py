"""User settings helpers for onboarding and setup completeness."""

from __future__ import annotations

from decimal import Decimal

from app.models import UserSettings

METHOD_LABELS = {
    1: "الحول المستقل لكل مال",
    2: "موعد زكاة موحد",
}


def needs_setup(settings: UserSettings) -> bool:
    """True when required settings are still missing for accurate zakat."""
    if not settings.gold_price_per_gram or settings.gold_price_per_gram <= 0:
        return True
    if settings.preferred_method == 2 and settings.zakat_date is None:
        return True
    return False


def setup_checklist(settings: UserSettings) -> list[dict]:
    """Return setup steps with done/missing status for UI checklists."""
    steps = [
        {
            "id": "gold_price",
            "label": "سعر جرام الذهب",
            "done": bool(settings.gold_price_per_gram and settings.gold_price_per_gram > 0),
            "hint": "مطلوب لحساب النصاب وتقييم الذهب",
        },
        {
            "id": "currency",
            "label": "العملة",
            "done": bool(settings.currency and settings.currency.strip()),
            "hint": "مثال: ج.م ",
        },
        {
            "id": "method",
            "label": "طريقة حساب الزكاة",
            "done": settings.preferred_method in (1, 2),
            "hint": METHOD_LABELS.get(settings.preferred_method, ""),
        },
    ]
    if settings.preferred_method == 2:
        steps.append(
            {
                "id": "zakat_date",
                "label": "موعد الزكاة السنوي",
                "done": settings.zakat_date is not None,
                "hint": "مطلوب للطريقة الثانية",
            }
        )
    return steps
