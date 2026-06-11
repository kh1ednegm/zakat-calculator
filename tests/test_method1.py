from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.zakat_service import calculate_method1, hawl_completed

AS_OF = date(2026, 1, 1)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_hawl_completed_after_full_hijri_year():
    assert hawl_completed(date(2024, 1, 1), AS_OF) is True
    assert hawl_completed(date(2025, 12, 20), AS_OF) is False


def test_method1_includes_only_assets_with_completed_hawl():
    savings = [
        ns(amount=Decimal("10000"), date=date(2024, 1, 1), description="old"),
        ns(amount=Decimal("5000"), date=date(2025, 12, 20), description="new"),
    ]
    result = calculate_method1(savings, [], [], [], Decimal("50"), as_of=AS_OF)
    assert result.base_total == Decimal("10000.00")
    included = [line for line in result.lines if line.included]
    assert len(included) == 1


def test_method1_fifo_withdrawals_and_debts():
    savings = [
        ns(amount=Decimal("10000"), date=date(2024, 1, 1), description=None),
        ns(amount=Decimal("5000"), date=date(2025, 12, 20), description=None),
    ]
    withdrawals = [ns(amount=Decimal("2000"), date=date(2025, 6, 1), description=None)]
    debts = [ns(amount=Decimal("1000"), due_date=date(2026, 2, 1), description=None)]
    result = calculate_method1(savings, [], debts, withdrawals, Decimal("50"), as_of=AS_OF)
    # FIFO: 10000 - 2000 = 8000 (hawl completed), 5000 excluded (hawl not completed)
    assert result.base_total == Decimal("8000.00")
    assert result.net_total == Decimal("7000.00")
    # nisab = 85 x 50 = 4250 -> reached
    assert result.reached_nisab is True
    assert result.zakat_due == Decimal("175.00")


def test_method1_below_nisab_no_zakat():
    savings = [ns(amount=Decimal("1000"), date=date(2024, 1, 1), description=None)]
    result = calculate_method1(savings, [], [], [], Decimal("400"), as_of=AS_OF)
    # nisab = 34,000 > 1,000
    assert result.reached_nisab is False
    assert result.zakat_due == Decimal("0.00")


def test_method1_gold_hawl():
    gold = [
        ns(weight_grams=Decimal("100"), karat=24, purchase_date=date(2024, 1, 1), description=None),
        ns(weight_grams=Decimal("10"), karat=24, purchase_date=date(2025, 12, 25), description=None),
    ]
    result = calculate_method1([], gold, [], [], Decimal("400"), as_of=AS_OF)
    # Only the first asset completed its hawl: 100 x 400 = 40,000 >= nisab 34,000
    assert result.base_total == Decimal("40000.00")
    assert result.reached_nisab is True
    assert result.zakat_due == Decimal("1000.00")
