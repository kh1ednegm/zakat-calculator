from sqlalchemy.orm import Session


class UserScopedRepository:
    """Generic CRUD repository where every record is scoped to a single user.

    All queries filter by ``user_id`` so a user can never read or modify
    another user's records (application-level isolation, complemented by
    Supabase RLS policies at the database level).
    """

    model = None
    order_field: str | None = None

    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: str):
        query = self.db.query(self.model).filter(self.model.user_id == user_id)
        if self.order_field:
            query = query.order_by(getattr(self.model, self.order_field).desc())
        return query.all()

    def get(self, user_id: str, item_id: str):
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.id == item_id)
            .first()
        )

    def create(self, user_id: str, **data):
        obj = self.model(user_id=user_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, user_id: str, item_id: str, **data):
        obj = self.get(user_id, item_id)
        if obj is None:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, user_id: str, item_id: str) -> bool:
        obj = self.get(user_id, item_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
