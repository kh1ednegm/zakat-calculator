"""Zakat calculation engine.

Implements the two supported scholarly methods:

- Method 1 (الحول المستقل لكل مال): every savings deposit and every gold
  purchase tracks its own Hijri year (hawl). Only assets that completed a
  full Hijri year are included in the Zakat base.
- Method 2 (موعد زكاة موحد): all assets are aggregated on a single annual
  Zakat date chosen by the user.

Zakat rate: 2.5%. Nisab: 85 grams of gold at the current market price.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from hijridate import Gregorian, Hijri

NISAB_GOLD_GRAMS = Decimal("85")
ZAKAT_RATE = Decimal("0.025")
TWO_PLACES = Decimal("0.01")

DISCLAIMER = (
    "هذه الحاسبة أداة مساعدة لحساب الزكاة وفق آراء فقهية معتبرة "
    "ولا تغني عن استشارة أهل العلم عند الحاجة."
)


def money(value) -> Decimal:
    """Quantize a value to 2 decimal places."""
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def nisab_value(gold_price_per_gram) -> Decimal:
    """Nisab = 85 grams x current gold price per gram."""
    price = Decimal(gold_price_per_gram or 0)
    if price < 0:
        raise ValueError("سعر الذهب يجب أن يكون رقمًا غير سالب")
    return money(NISAB_GOLD_GRAMS * price)


def gold_value(weight_grams, karat, gold_price_per_gram) -> Decimal:
    """Current market value of a gold asset, adjusted for karat purity."""
    weight = Decimal(weight_grams)
    price = Decimal(gold_price_per_gram or 0)
    karat = int(karat)
    if weight <= 0:
        raise ValueError("وزن الذهب يجب أن يكون أكبر من صفر")
    if not 1 <= karat <= 24:
        raise ValueError("العيار يجب أن يكون بين 1 و24")
    purity = Decimal(karat) / Decimal(24)
    return money(weight * price * purity)


def hawl_due_date(start: date) -> date:
    """Gregorian date on which one full Hijri year is completed."""
    hijri = Gregorian(start.year, start.month, start.day).to_hijri()
    day = hijri.day
    while day >= 1:
        try:
            g = Hijri(hijri.year + 1, hijri.month, day).to_gregorian()
            return date(g.year, g.month, g.day)
        except (ValueError, OverflowError):
            day -= 1
    raise ValueError("تعذر حساب تاريخ الحول")


def hawl_completed(start: date, as_of: date | None = None) -> bool:
    """Has one full Hijri year passed since ``start``?"""
    as_of = as_of or date.today()
    return as_of >= hawl_due_date(start)


@dataclass
class AssetLine:
    kind: str  # "savings" | "gold" | "withdrawals"
    description: str
    start_date: date
    value: Decimal
    included: bool
    reason: str


@dataclass
class MethodResult:
    method: int
    as_of: date
    base_total: Decimal
    debts_total: Decimal
    net_total: Decimal
    nisab: Decimal
    reached_nisab: bool
    zakat_due: Decimal
    lines: list


def _apply_withdrawals_fifo(savings, withdrawals):
    """Deduct total withdrawals from the oldest deposits first (FIFO).

    Returns a list of ``(saving, remaining_amount)`` tuples.
    """
    remaining = sum((Decimal(w.amount) for w in withdrawals), Decimal(0))
    result = []
    for saving in sorted(savings, key=lambda s: s.date):
        amount = Decimal(saving.amount)
        if remaining > 0:
            used = min(amount, remaining)
            amount -= used
            remaining -= used
        result.append((saving, amount))
    return result


def calculate_method1(
    savings, gold_assets, debts, withdrawals, gold_price_per_gram, as_of: date | None = None
) -> MethodResult:
    """Method 1: independent hawl per asset."""
    as_of = as_of or date.today()
    nisab = nisab_value(gold_price_per_gram)
    lines: list[AssetLine] = []
    base = Decimal(0)

    for saving, amount in _apply_withdrawals_fifo(savings, withdrawals):
        label = saving.description or "إيداع"
        if amount <= 0:
            lines.append(
                AssetLine("savings", label, saving.date, money(0), False, "استُهلك المبلغ بالسحوبات")
            )
            continue
        done = hawl_completed(saving.date, as_of)
        if done:
            reason = "أتم الحول الهجري"
            base += amount
        else:
            reason = f"لم يتم الحول (يكتمل في {hawl_due_date(saving.date):%Y-%m-%d})"
        lines.append(AssetLine("savings", label, saving.date, money(amount), done, reason))

    for gold in gold_assets:
        value = gold_value(gold.weight_grams, gold.karat, gold_price_per_gram)
        label = gold.description or f"ذهب عيار {gold.karat}"
        done = hawl_completed(gold.purchase_date, as_of)
        if done:
            reason = "أتم الحول الهجري"
            base += value
        else:
            reason = f"لم يتم الحول (يكتمل في {hawl_due_date(gold.purchase_date):%Y-%m-%d})"
        lines.append(AssetLine("gold", label, gold.purchase_date, value, done, reason))

    debts_total = money(sum((Decimal(d.amount) for d in debts), Decimal(0)))
    net = money(base) - debts_total
    if net < 0:
        net = Decimal("0.00")
    reached = nisab > 0 and net >= nisab
    zakat = money(net * ZAKAT_RATE) if reached else Decimal("0.00")
    return MethodResult(1, as_of, money(base), debts_total, money(net), nisab, reached, zakat, lines)


def calculate_method2(
    savings,
    gold_assets,
    debts,
    withdrawals,
    gold_price_per_gram,
    zakat_date: date | None = None,
    as_of: date | None = None,
) -> MethodResult:
    """Method 2: unified annual Zakat date, all assets aggregated."""
    as_of = as_of or zakat_date or date.today()
    nisab = nisab_value(gold_price_per_gram)
    lines: list[AssetLine] = []

    savings_total = sum((Decimal(s.amount) for s in savings), Decimal(0))
    withdrawals_total = sum((Decimal(w.amount) for w in withdrawals), Decimal(0))
    net_savings = savings_total - withdrawals_total
    if net_savings < 0:
        net_savings = Decimal(0)

    for saving in savings:
        lines.append(
            AssetLine(
                "savings",
                saving.description or "إيداع",
                saving.date,
                money(saving.amount),
                True,
                "يُجمع في موعد الزكاة الموحد",
            )
        )

    gold_total = Decimal(0)
    for gold in gold_assets:
        value = gold_value(gold.weight_grams, gold.karat, gold_price_per_gram)
        gold_total += value
        lines.append(
            AssetLine(
                "gold",
                gold.description or f"ذهب عيار {gold.karat}",
                gold.purchase_date,
                value,
                True,
                "يُقوّم بسعر السوق الحالي",
            )
        )

    if withdrawals_total > 0:
        lines.append(
            AssetLine(
                "withdrawals",
                "إجمالي السحوبات",
                as_of,
                money(withdrawals_total),
                True,
                "تُخصم من إجمالي المدخرات",
            )
        )

    base = money(net_savings + gold_total)
    debts_total = money(sum((Decimal(d.amount) for d in debts), Decimal(0)))
    net = base - debts_total
    if net < 0:
        net = Decimal("0.00")
    reached = nisab > 0 and net >= nisab
    zakat = money(net * ZAKAT_RATE) if reached else Decimal("0.00")
    return MethodResult(2, as_of, base, debts_total, money(net), nisab, reached, zakat, lines)


def dashboard_summary(
    savings, gold_assets, debts, withdrawals, gold_price_per_gram, zakat_date: date | None = None
) -> dict:
    """Aggregated totals for the dashboard, with a Method 2 Zakat estimate."""
    m2 = calculate_method2(
        savings, gold_assets, debts, withdrawals, gold_price_per_gram, zakat_date=zakat_date
    )
    savings_total = money(sum((Decimal(s.amount) for s in savings), Decimal(0)))
    withdrawals_total = money(sum((Decimal(w.amount) for w in withdrawals), Decimal(0)))
    net_savings = savings_total - withdrawals_total
    if net_savings < 0:
        net_savings = Decimal("0.00")
    gold_total = money(
        sum(
            (gold_value(g.weight_grams, g.karat, gold_price_per_gram) for g in gold_assets),
            Decimal(0),
        )
    )
    return {
        "savings_total": savings_total,
        "withdrawals_total": withdrawals_total,
        "net_savings": net_savings,
        "gold_total": gold_total,
        "debts_total": m2.debts_total,
        "net_wealth": m2.net_total,
        "nisab": m2.nisab,
        "reached_nisab": m2.reached_nisab,
        "zakat_estimate": m2.zakat_due,
    }
