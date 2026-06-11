from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.zakat_service import calculate_method2

AS_OF = date(2026, 1, 1)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_method2_aggregates_everything_on_unified_date():
    savings = [ns(amount=Decimal("20000"), date=date(2025, 11, 1), description=None)]
    withdrawals = [ns(amount=Decimal("5000"), date=date(2025, 12, 1), description=None)]
    gold = [ns(weight_grams=Decimal("10"), karat=24, purchase_date=date(2025, 12, 30), description=None)]
    debts = [ns(amount=Decimal("2000"), due_date=date(2026, 3, 1), description=None)]
    result = calculate_method2(savings, gold, debts, withdrawals, Decimal("100"), as_of=AS_OF)
    # savings 20000 - withdrawals 5000 = 15000 ; gold = 10 x 100 = 1000 ; base = 16000
    assert result.base_total == Decimal("16000.00")
    # net = 16000 - 2000 = 14000 ; nisab = 8500 -> reached
    assert result.net_total == Decimal("14000.00")
    assert result.reached_nisab is True
    assert result.zakat_due == Decimal("350.00")


def test_method2_includes_recent_assets_unlike_method1():
    # Asset added yesterday is still aggregated in method 2
    savings = [ns(amount=Decimal("50000"), date=date(2025, 12, 31), description=None)]
    result = calculate_method2(savings, [], [], [], Decimal("400"), as_of=AS_OF)
    assert result.base_total == Decimal("50000.00")
    assert result.reached_nisab is True  # nisab = 34,000
    assert result.zakat_due == Decimal("1250.00")


def test_method2_below_nisab_no_zakat():
    savings = [ns(amount=Decimal("2000"), date=date(2025, 1, 1), description=None)]
    result = calculate_method2(savings, [], [], [], Decimal("400"), as_of=AS_OF)
    assert result.reached_nisab is False
    assert result.zakat_due == Decimal("0.00")


def test_method2_debts_cannot_make_net_negative():
    savings = [ns(amount=Decimal("1000"), date=date(2025, 1, 1), description=None)]
    debts = [ns(amount=Decimal("5000"), due_date=date(2026, 1, 1), description=None)]
    result = calculate_method2(savings, [], debts, [], Decimal("400"), as_of=AS_OF)
    assert result.net_total == Decimal("0.00")
    assert result.zakat_due == Decimal("0.00")
