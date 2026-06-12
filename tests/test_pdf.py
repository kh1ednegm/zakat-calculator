from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.pdf_service import FONT_NAME, generate_report
from app.services.zakat_service import calculate_method1, calculate_method2


def test_pdf_generates_valid_bytes():
    user = SimpleNamespace(full_name="محمد أحمد")
    settings = SimpleNamespace(currency="ر.س", gold_price_per_gram=Decimal("250"))
    savings = [
        SimpleNamespace(date=date(2024, 1, 1), amount=Decimal("10000"), description="راتب")
    ]
    m1 = calculate_method1(savings, [], [], [], Decimal("250"))
    m2 = calculate_method2(savings, [], [], [], Decimal("250"))

    pdf = generate_report(
        user=user,
        user_settings=settings,
        savings=savings,
        gold_assets=[],
        debts=[],
        withdrawals=[],
        m1=m1,
        m2=m2,
    )

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
    assert FONT_NAME == "Amiri"
