from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.settings_service import needs_setup, setup_checklist


def _settings(**kwargs):
    defaults = {
        "gold_price_per_gram": Decimal("0"),
        "currency": "ر.س",
        "preferred_method": 1,
        "zakat_date": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_needs_setup_when_gold_price_missing():
    assert needs_setup(_settings()) is True
    assert needs_setup(_settings(gold_price_per_gram=Decimal("250"))) is False


def test_needs_setup_when_method2_without_date():
    s = _settings(gold_price_per_gram=Decimal("250"), preferred_method=2)
    assert needs_setup(s) is True
    assert needs_setup(_settings(gold_price_per_gram=Decimal("250"), preferred_method=2, zakat_date=date(2025, 3, 1))) is False


def test_setup_checklist_includes_zakat_date_for_method2():
    steps = setup_checklist(_settings(preferred_method=2))
    assert any(step["id"] == "zakat_date" for step in steps)
