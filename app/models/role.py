from app import db
from app.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = db.Column("name", db.String(50), nullable=False, unique=True)
    description = db.Column("description", db.String(128), nullable=True)
    users = db.relationship("User", backref="role", lazy=True)

    def get_name(self):
        return self.name

    def as_dict(self):
        return {
            "name": self.name,
            "description": self.description,
        }
