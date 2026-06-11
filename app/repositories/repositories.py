from sqlalchemy.orm import Session

from app.models import Debt, GoldAsset, Saving, User, UserSettings, Withdrawal
from app.repositories.base import UserScopedRepository


class SavingsRepository(UserScopedRepository):
    model = Saving
    order_field = "date"


class GoldRepository(UserScopedRepository):
    model = GoldAsset
    order_field = "purchase_date"


class DebtRepository(UserScopedRepository):
    model = Debt
    order_field = "due_date"


class WithdrawalRepository(UserScopedRepository):
    model = Withdrawal
    order_field = "date"


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: str) -> UserSettings:
        obj = self.db.get(UserSettings, user_id)
        if obj is None:
            obj = UserSettings(user_id=user_id)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def update(self, user_id: str, **data) -> UserSettings:
        obj = self.get_or_create(user_id)
        for key, value in data.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
