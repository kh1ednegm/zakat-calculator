from sqlalchemy.orm import Session

from app.models import User, UserSettings
from app.security import hash_password, verify_password


def register(db: Session, *, email: str, full_name: str, password: str) -> User:
    """Create a new user with a hashed password and default settings."""
    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        raise ValueError("البريد الإلكتروني مسجل مسبقًا")
    user = User(email=email, full_name=full_name, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    db.add(UserSettings(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, *, email: str, password: str) -> User | None:
    """Return the user when credentials are valid, otherwise None."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
