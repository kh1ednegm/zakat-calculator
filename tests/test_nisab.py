from decimal import Decimal

import pytest

from app.services.zakat_service import nisab_value


def test_nisab_basic():
    # 85 grams x 400 = 34,000
    assert nisab_value(Decimal("400")) == Decimal("34000.00")


def test_nisab_zero_price():
    assert nisab_value(Decimal("0")) == Decimal("0.00")


def test_nisab_none_price_treated_as_zero():
    assert nisab_value(None) == Decimal("0.00")


def test_nisab_negative_price_raises():
    with pytest.raises(ValueError):
        nisab_value(Decimal("-1"))
