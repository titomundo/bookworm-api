from app.database.repository import (BusinessRepository, LocationRepository,
                                     ReservationRepository, UserRepository)
from app.models import business, location
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

    """Business Facade Methods"""

    def create_business(self, business_data) -> Business:
        business = Business(**business_data)
        self.business_repo.add(business)
        return business

    def get_business(self, business_id) -> Business | None:
        return self.business_repo.get(business_id)

    def get_all_businesses(self) -> list[Business]:
        return self.business_repo.get_all()

    def update_business(self, business_id, business_data) -> Business | None:
        return self.business_repo.update(business_id, business_data)

    def get_business_by_email(self, email) -> Business | None:
        return self.business_repo.get_business_by_email(email)

    def delete_business(self, business_id):
        self.business_repo.delete(business_id)

    """Location Facade Methods"""

    def create_location(self, location_data) -> Location:
        location = Location(**location_data)
        self.location_repo.add(location)
        return location

    def get_location(self, location_id) -> Location | None:
        return self.location_repo.get(location_id)

    def get_all_locations(self) -> list[Location]:
        return self.location_repo.get_all()

    def update_location(self, location_id, location_data) -> Location | None:
        return self.location_repo.update(location_id, location_data)

    def delete_location(self, location_id):
        self.location_repo.delete(location_id)

    """Reservation Facade Methods"""

    def create_reservation(self, reservation_data) -> Reservation:
        reservation = Reservation(**reservation_data)
        self.reservation_repo.add(reservation)
        return reservation

    def get_reservation(self, reservation_id) -> Reservation | None:
        return self.reservation_repo.get(reservation_id)

    def get_all_reservations(self) -> list[Reservation]:
        return self.reservation_repo.get_all()

    def update_reservation(
        self, reservation_id, reservation_data
    ) -> Reservation | None:
        return self.reservation_repo.update(reservation_id, reservation_data)

    def delete_reservation(self, reservation_id):
        self.reservation_repo.delete(reservation_id)
