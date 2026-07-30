from datetime import datetime

from sqlalchemy.orm import validates

from app import db
from app.models.base import BaseModel
from app.models.location import Location


class Reservation(BaseModel):
    __tablename__ = "reservations"

    client_name = db.Column("client_name", db.String(100), nullable=False)
    reason = db.Column("reason", db.String(512), nullable=False)
    date = db.Column("date", db.DateTime(), nullable=False)
    slot = db.Column("slot", db.Integer, nullable=False)
    status = db.Column("status", db.String(64), nullable=False)
    user_id = db.Column(
        "user_id", db.String(36), db.ForeignKey("users.id"), nullable=False
    )
    location_id = db.Column(
        "location_id", db.String(36), db.ForeignKey("locations.id"), nullable=False
    )

    @validates("client_name")
    def validate_client_name(self, key, client_name):
        if len(client_name) > 100:
            raise ValueError("Client Name has a maximum length of 100 characters")

        return client_name

    @validates("reason")
    def validate_reason(self, key, reason):
        if len(reason) > 512:
            raise ValueError("Reason has a maximum length of 512 characters")

        return reason

    @validates("date")
    def validate_date(self, key, date):
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M")

        if not date:
            raise ValueError("Invalid Date")

        return date

    @validates("status")
    def validate_status(self, key, status):
        if len(status) > 64:
            raise ValueError("Status has a maximum length of 64 characters")

        return status

    def as_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "reason": self.reason,
            "date": self.date.isoformat(),
            "slot": self.slot,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
