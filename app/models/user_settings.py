import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    gold_price_per_gram: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="ر.س", nullable=False)
    zakat_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    preferred_method: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="settings")
