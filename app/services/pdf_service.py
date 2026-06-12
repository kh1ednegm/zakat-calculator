"""PDF report generation with Arabic (RTL) text support.

Uses reportlab + arabic-reshaper + python-bidi. The Amiri font is loaded
from app/static/fonts/ when available; it is auto-downloaded on first use
if missing. Without a TTF font, Arabic text cannot render correctly.
"""

from __future__ import annotations

import io
import os
import re
import urllib.request
from datetime import date
from decimal import Decimal

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.zakat_service import DISCLAIMER, gold_value

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

_FONT_DIR = os.path.join("app", "static", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "Amiri-Regular.ttf")
_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
_FONT_CANDIDATES = (
    _FONT_PATH,
    "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
)

FONT_NAME = "Helvetica"


def _ensure_amiri_font() -> str | None:
    """Return the path to an Arabic-capable TTF font, downloading Amiri if needed."""
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path

    try:
        os.makedirs(_FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(_FONT_URL, _FONT_PATH)
        if os.path.exists(_FONT_PATH) and os.path.getsize(_FONT_PATH) > 0:
            return _FONT_PATH
    except OSError:
        pass
    return None


def _register_font() -> None:
    global FONT_NAME
    font_path = _ensure_amiri_font()
    if font_path and os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("Amiri", font_path))
            FONT_NAME = "Amiri"
        except Exception:
            FONT_NAME = "Helvetica"
    else:
        FONT_NAME = "Helvetica"


_register_font()

_TITLE = ParagraphStyle("title", fontName=FONT_NAME, fontSize=18, alignment=TA_CENTER, spaceAfter=12)
_HEADING = ParagraphStyle("heading", fontName=FONT_NAME, fontSize=14, alignment=TA_RIGHT, spaceBefore=12, spaceAfter=6)
_BODY = ParagraphStyle("body", fontName=FONT_NAME, fontSize=11, alignment=TA_RIGHT, leading=16)
_CELL = ParagraphStyle("cell", fontName=FONT_NAME, fontSize=10, alignment=TA_CENTER, leading=14)


def _ar(text) -> str:
    """Reshape Arabic text and apply the bidi algorithm for correct rendering."""
    return get_display(arabic_reshaper.reshape(str(text)))


def _pdf_text(text) -> str:
    """Shape Arabic text only; leave numbers, dates, and Latin text unchanged."""
    s = str(text)
    if _ARABIC_RE.search(s):
        return _ar(s)
    return s


def _fmt(value) -> str:
    return f"{Decimal(value):,.2f}"


def _table(rows, col_widths=None) -> Table:
    """Build an RTL-ordered table (columns defined right-to-left, stored left-to-right)."""
    data = [[_pdf_text(cell) for cell in reversed(row)] for row in rows]
    table = Table(data, colWidths=col_widths, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D4A42")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2EAE7")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7F6")]),
            ]
        )
    )
    return table


def generate_report(*, user, user_settings, savings, gold_assets, debts, withdrawals, m1, m2) -> bytes:
    """Build the full Zakat PDF report and return it as bytes."""
    _register_font()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Zakat Report",
    )
    currency = user_settings.currency or "ر.س"
    price = user_settings.gold_price_per_gram or Decimal("0")
    elements = []

    elements.append(Paragraph(_pdf_text("تقرير حساب الزكاة"), _TITLE))
    elements.append(
        Paragraph(
            _pdf_text(f"الاسم: {user.full_name} | تاريخ التقرير: {date.today():%Y-%m-%d}"),
            _BODY,
        )
    )
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(_pdf_text("ملخص المدخرات"), _HEADING))
    rows = [["التاريخ", "الوصف", f"المبلغ ({currency})"]]
    for s in savings:
        rows.append([f"{s.date}", s.description or "-", _fmt(s.amount)])
    rows.append(["الإجمالي", "", _fmt(sum((Decimal(s.amount) for s in savings), Decimal(0)))])
    elements.append(_table(rows))

    elements.append(Paragraph(_pdf_text("ملخص السحوبات"), _HEADING))
    rows = [["التاريخ", "الوصف", f"المبلغ ({currency})"]]
    for w in withdrawals:
        rows.append([f"{w.date}", w.description or "-", _fmt(w.amount)])
    rows.append(["الإجمالي", "", _fmt(sum((Decimal(w.amount) for w in withdrawals), Decimal(0)))])
    elements.append(_table(rows))

    elements.append(Paragraph(_pdf_text("ملخص الذهب"), _HEADING))
    rows = [["تاريخ الشراء", "العيار", "الوزن (جم)", f"القيمة ({currency})"]]
    gold_total = Decimal(0)
    for g in gold_assets:
        value = gold_value(g.weight_grams, g.karat, price)
        gold_total += value
        rows.append([f"{g.purchase_date}", str(g.karat), _fmt(g.weight_grams), _fmt(value)])
    rows.append(["الإجمالي", "", "", _fmt(gold_total)])
    elements.append(_table(rows))

    elements.append(Paragraph(_pdf_text("ملخص الديون"), _HEADING))
    rows = [["تاريخ الاستحقاق", "الوصف", f"المبلغ ({currency})"]]
    for d in debts:
        rows.append([f"{d.due_date}", d.description or "-", _fmt(d.amount)])
    rows.append(["الإجمالي", "", _fmt(sum((Decimal(d.amount) for d in debts), Decimal(0)))])
    elements.append(_table(rows))

    elements.append(Paragraph(_pdf_text("حساب النصاب"), _HEADING))
    elements.append(
        Paragraph(
            _pdf_text(
                f"سعر جرام الذهب: {_fmt(price)} {currency} | "
                f"النصاب (85 جم): {_fmt(m2.nisab)} {currency}"
            ),
            _BODY,
        )
    )

    elements.append(Paragraph(_pdf_text("نتائج حساب الزكاة"), _HEADING))
    rows = [
        ["البيان", "الطريقة الأولى: الحول المستقل", "الطريقة الثانية: موعد موحد"],
        ["الوعاء الزكوي", _fmt(m1.base_total), _fmt(m2.base_total)],
        ["الديون المخصومة", _fmt(m1.debts_total), _fmt(m2.debts_total)],
        ["الصافي", _fmt(m1.net_total), _fmt(m2.net_total)],
        ["بلوغ النصاب", "نعم" if m1.reached_nisab else "لا", "نعم" if m2.reached_nisab else "لا"],
        [f"الزكاة المستحقة ({currency})", _fmt(m1.zakat_due), _fmt(m2.zakat_due)],
    ]
    elements.append(_table(rows))

    elements.append(Spacer(1, 14))
    elements.append(Paragraph(_pdf_text(DISCLAIMER), _BODY))

    doc.build(elements)
    return buffer.getvalue()
