import re

from sqlalchemy.orm import validates

from app import bcrypt, db
from app.models.base import BaseModel


class User(BaseModel):
    _emails = set()
    _email_regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    __tablename__ = "users"

    first_name = db.Column("first_name", db.String(50), nullable=False)
    last_name = db.Column("last_name", db.String(50), nullable=False)
    email = db.Column("email", db.String(120), nullable=False, unique=True)
    password = db.Column("password", db.String(128), nullable=False)
    is_admin = db.Column("is_admin", db.Boolean, default=False)

    @validates("first_name")
    def validate_first_name(self, key, first_name):
        if len(first_name) > 50:
            raise ValueError("First name has a maximum length of 50 characters")

        if not first_name.strip():
            raise ValueError("First name cannot be empty")

        return first_name

    @validates("last_name")
    def validate_last_name(self, key, last_name):
        if len(last_name) > 50:
            raise ValueError("Last name has a maximum length of 50 characters")

        if not last_name.strip():
            raise ValueError("Last name cannot be empty")

        return last_name

    @validates("email")
    def validate_email(self, key, email):
        if not re.match(self._email_regex, email) or not email.strip():
            raise ValueError("Not a valid email")

        if email in User._emails:
            raise ValueError("Email is already in use")

        return email

    def validate_password(self, password):
        """Set password using hash_password"""
        self.hash_password(password)

    def hash_password(self, new_password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    def as_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
