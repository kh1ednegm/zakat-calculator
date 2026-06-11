import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, Field


class SavingIn(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    date: dt.date
    description: str | None = Field(default=None, max_length=255)


class GoldIn(BaseModel):
    weight_grams: Decimal = Field(gt=0, le=Decimal("9999999"))
    karat: int = Field(ge=1, le=24)
    purchase_date: dt.date
    description: str | None = Field(default=None, max_length=255)


class DebtIn(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    due_date: dt.date
    description: str | None = Field(default=None, max_length=255)


class WithdrawalIn(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    date: dt.date
    description: str | None = Field(default=None, max_length=255)


class SettingsIn(BaseModel):
    gold_price_per_gram: Decimal = Field(ge=0, le=Decimal("9999999"))
    currency: str = Field(min_length=1, max_length=10)
    zakat_date: dt.date | None = None
    preferred_method: int = Field(ge=1, le=2)
