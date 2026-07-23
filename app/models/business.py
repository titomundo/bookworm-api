from sqlalchemy.orm import validates

from app import db, is_valid_email
from app.models.base import BaseModel


class Business(BaseModel):
    __tablename__ = "businesses"

    name = db.Column("name", db.String(128), nullable=False)
    description = db.Column("description", db.String(512), nullable=False)
    email = db.Column("email", db.String(120), nullable=False, unique=True)
    phone_number = db.Column("phone_number", db.String(12), nullable=False, unique=True)
    owner_id = db.Column(
        "owner_id", db.String(36), db.ForeignKey("users.id"), nullable=False
    )

    @validates("name")
    def validate_name(self, key, name):
        if len(name) > 128:
            raise ValueError("Name has a maximum length of 128 characters")

        return name

    @validates("description")
    def validate_description(self, key, description):
        if len(description) > 128:
            raise ValueError("Description has a maximum length of 512 characters")

        return description

    @validates("email")
    def validate_email(self, key, email):
        if not is_valid_email(email):
            raise ValueError("Not a valid email")

        # check if email is registed
        if self.query.filter(Business.email == email).first():
            raise ValueError("Email already registerd")

        return email

    @validates("phone_number")
    def validate_phone_number(self, key, phone_number):
        if len(phone_number) > 12:
            raise ValueError("Phone number has maximum length of 12 digits")

        if not phone_number.isdigit():
            raise ValueError("Phone number must contain only digits")

        # check if phone_number is registed
        if self.query.filter(Business.phone_number == phone_number).first():
            raise ValueError("Phone number already registerd")

        return phone_number

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
