import re

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restx import Namespace, Resource, fields

from app.models.location import Location
from app.models.reservation import Reservation
from app.services import facade

api = Namespace("reservations", description="Reservations operations")

reservation_model = api.model(
    "Reservation",
    {
        "client_name": fields.String(
            required=True, description="Name of the client assigned to the reservation"
        ),
        "reason": fields.String(
            required=True, description="Brief reason for the reservation"
        ),
        "date": fields.DateTime(required=True, description="Date of the reservation"),
        "slot": fields.Integer(
            required=True, description="Slot number of the reservation"
        ),
        "status": fields.String(required=True, description="Status of the reservation"),
        "location_id": fields.String(required=True, description="ID of the location"),
    },
)


def is_slot_occupied(slot, location_id):
    reservation = (
        Reservation.query.filter(Reservation.slot == slot)
        .filter((Reservation.status == "pending") | (Reservation.status == "ongoing"))
        .first()
    )

    if reservation.location_id == location_id:
        return True

    return False


@api.route("/")
class ReservationList(Resource):
    @jwt_required()
    @api.expect(reservation_model, validate=True)
    @api.response(201, "Reservation successfully booked")
    @api.response(400, "Invalid input data")
    @api.response(403, "Unauthorized")
    @api.response(404, "Resource not found")
    def post(self):
        """Create reservation"""
        reservation_data = api.payload
        current_user = facade.get_user(get_jwt_identity())
        location_id = reservation_data.get("location_id")
        location = facade.get_location(location_id)
        slot = reservation_data.get("slot")

        if not current_user or not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        if not location:
            return {"error": "location not found"}, 404

        if slot > location.capacity:
            return {"error": "Out of bounds slot"}, 400

        if is_slot_occupied(slot, location_id):
            return {"error": "Slot occupied"}, 400

        try:
            reservation_data["user_id"] = current_user.id
            new_reservation = facade.create_reservation(reservation_data)
        except (ValueError, TypeError) as e:
            return {"error": str(e)}, 400

        return new_reservation.as_dict(), 200

    @jwt_required()
    @api.response(200, "List of reservations")
    @api.response(403, "Invalid credentials")
    def get(self):
        current_user = facade.get_user(get_jwt_identity())
        locations = current_user.locations
        reservations = []

        for location in locations:
            for reservation in location.reservations:
                reservations.append(reservation.as_dict())

        return reservations, 200


@api.route("/<reservation_id>")
class ReservationResource(Resource):
    @jwt_required()
    @api.response(200, "Reservation details retrieved successfully")
    @api.response(403, "Unauthorized")
    @api.response(404, "Resource not found")
    def get(self, reservation_id):
        current_user = facade.get_user(get_jwt_identity())
        reservation = facade.get_reservation(reservation_id)

        if not current_user:
            return {"error": "User not found"}, 404

        if not reservation:
            return {"error": "Reservation not found"}, 404

        locations = [l.id for l in current_user.locations]

        if not reservation.location_id in locations:
            return {"error": "Unauthorized"}, 403

        return reservation.as_dict(), 200

    @jwt_required()
    @api.response(200, "Reservation details updated successfully")
    @api.response(403, "Unauthorized")
    @api.response(404, "Resource not found")
    def put(self, reservation_id):
        """Update reservation details"""
        current_user = facade.get_user(get_jwt_identity())
        reservation = facade.get_reservation(reservation_id)
        reservation_data = api.payload
        slot = reservation_data.get("slot")

        if not current_user:
            return {"error": "Unauthorized"}, 403

        if not reservation:
            return {"error": "Reservation not found"}, 404

        locations = [l.id for l in current_user.locations]

        if not reservation.location_id in locations:
            return {"error": "Unauthorized"}, 403

        if reservation_data.get("location_id") or reservation_data.get("user_id"):
            return {"error": "Non mutable fields"}, 403

        location = facade.get_location(reservation.location_id)

        if slot and slot > location.capacity:
            return {"error": "Out of bounds slot"}, 400

        if is_slot_occupied(slot):
            return {"error": "Slot occupied"}, 400

        try:
            facade.update_reservation(reservation_id, reservation_data)
        except (ValueError, TypeError) as e:
            return {"error": str(e)}, 400

        return {"message": "Reservation updated successfully"}, 200

    @jwt_required()
    @api.response(200, "Reservation deleted successfully")
    @api.response(403, "Unauthorized")
    @api.response(404, "Resource not found")
    def delete(self, reservation_id):
        """Delete reservation"""
        current_user = facade.get_user(get_jwt_identity())
        reservation = facade.get_reservation(reservation_id)

        if not current_user or not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        if not reservation:
            return {"error": "Reservation not found"}, 404

        locations = [l.id for l in current_user.locations]
        if not reservation.location_id in locations:
            return {"error": "Unauthorized"}, 403

        facade.delete_reservation(reservation_id)
        return {"message": "Reservation deleted successfully"}, 200
