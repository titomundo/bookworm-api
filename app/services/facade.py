from app.database.repository import (BusinessRepository, LocationRepository,
                                     ReservationRepository, UserRepository)
from app.models.business import Business
from app.models.location import Location
from app.models.reservation import Reservation
from app.models.user import User


class Facade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.business_repo = BusinessRepository()
        self.location_repo = LocationRepository()
        self.reservation_repo = ReservationRepository()

    """User Facade Methods"""

    def create_user(self, user_data) -> User:
        user = User(**user_data)
        user.hash_password(user_data["password"])
        self.user_repo.add(user)
        return user

    def get_user(self, user_id) -> User | None:
        return self.user_repo.get(user_id)

    def get_all_users(self) -> list[User]:
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data) -> User | None:
        return self.user_repo.update(user_id, user_data)

    def get_user_by_email(self, email) -> User | None:
        return self.user_repo.get_user_by_email(email)
