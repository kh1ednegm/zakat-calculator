from decimal import Decimal

import pytest

from app.services.zakat_service import gold_value


def test_gold_value_24k():
    # 10 g x 400 x (24/24) = 4,000
    assert gold_value(Decimal("10"), 24, Decimal("400")) == Decimal("4000.00")


def test_gold_value_18k_purity_adjustment():
    # 10 g x 400 x (18/24) = 3,000
    assert gold_value(Decimal("10"), 18, Decimal("400")) == Decimal("3000.00")


def test_gold_value_21k():
    # 10 g x 400 x (21/24) = 3,500
    assert gold_value(Decimal("10"), 21, Decimal("400")) == Decimal("3500.00")


def test_gold_value_zero_weight_raises():
    with pytest.raises(ValueError):
        gold_value(Decimal("0"), 24, Decimal("400"))


def test_gold_value_invalid_karat_raises():
    with pytest.raises(ValueError):
        gold_value(Decimal("10"), 25, Decimal("400"))
