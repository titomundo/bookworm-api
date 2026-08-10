from sqlalchemy.orm import validates

from app import db
from app.models.base import BaseModel


class Location(BaseModel):
    __tablename__ = "locations"

    name = db.Column("name", db.String(128), nullable=False)
    description = db.Column("description", db.String(512), nullable=False)
    capacity = db.Column(
        db.Integer,
        db.CheckConstraint("capacity > 0 AND capacity < 101"),
        nullable=False,
    )
    owner_id = db.Column("owner_id", db.String(36), db.ForeignKey("users.id"), nullable=False)
    business_id = db.Column(
        "business_id", db.String(36), db.ForeignKey("businesses.id"), nullable=False
    )

    reservations = db.relationship("Reservation", backref="Location", lazy=True)

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

    @validates("capacity")
    def validate_capacity(self, key, capacity):
        if capacity < 1 or capacity >= 100:
            raise ValueError("Capacity must be between 1 and 100")

        return capacity

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capacity": self.capacity,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
