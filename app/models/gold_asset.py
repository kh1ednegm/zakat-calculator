import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import generate_uuid


class GoldAsset(Base):
    __tablename__ = "gold_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    weight_grams: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    karat: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
