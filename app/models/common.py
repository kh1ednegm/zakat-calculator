import uuid


def generate_uuid() -> str:
    """Generate a string UUID usable as a primary key on any database."""
    return str(uuid.uuid4())
