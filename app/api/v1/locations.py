from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restx import Namespace, Resource, fields

from app.services import facade

api = Namespace("locations", description="Location operations")

location_model = api.model(
    "Location",
    {
        "name": fields.String(required=True, descripion="Name of the location"),
        "description": fields.String(required=False, description="Description"),
        "capacity": fields.Integer(
            required=True, description="Max number of tables, offices, slots, etc"
        ),
        "business_id": fields.String(required=True, description="ID of the business"),
    },
)


@api.route("/")
class LocationList(Resource):
    @jwt_required()
    @api.expect(location_model, validate=True)
    @api.response(201, "Business successfully created")
    @api.response(400, "Invalid input data")
    @api.response(403, "Unauthorized")
    @api.response(404, "Location or User not found")
    def post(self):
        """Create new location"""
        location_data = api.payload
        current_user = facade.get_user(get_jwt_identity())
        business = facade.get_business(location_data.get("business_id"))

        if not current_user:
            return {"error": "user not found"}, 404

        if not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        if not business:
            return {"error": "business not found"}, 404

        if current_user.id != business.owner_id:
            return {"error": "Unauthorized"}, 403

        try:
            location_data["owner_id"] = current_user.id
            new_location = facade.create_location(location_data)
        except ValueError as e:
            return {"error": str(e)}, 400

        return new_location.as_dict(), 200

    @api.response(200, "List of businesses")
    @api.response(403, "Invalid credentials")
    @jwt_required()
    def get(self):
        """Get list of all businesses for the current user"""
        current_user = facade.get_user(get_jwt_identity())

        if not current_user:
            return {"error": "invalid credentials"}, 403

        locations = [l.as_dict() for l in current_user.locations]
        return locations, 200


@api.route("/<location_id>")
class LocationResource(Resource):
    @jwt_required()
    @api.response(200, "Location details retrieved successfully")
    @api.response(403, "Unauthorized")
    @api.response(404, "Location not found")
    def get(self, location_id):
        """Get location by ID"""
        current_user = facade.get_user(get_jwt_identity())
        location = facade.get_location(location_id)

        if not current_user:
            return {"error": "user not found"}, 404

        if not location:
            return {"error": "Business not found"}, 404

        if current_user.id != location.owner_id:
            return {"error": "Unauthorized"}, 403

        return location.as_dict(), 200

    @jwt_required()
    @api.response(200, "Location deleted successfully")
    @api.response(404, "Location or user not found")
    @api.response(403, "Unauthorized")
    def delete(self, location_id):
        """Delete a location"""
        current_user = facade.get_user(get_jwt_identity())
        location = facade.get_location(location_id)

        if not current_user:
            return {"error": "user not found"}, 404

        if not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        if not location:
            return {"error": "Business not found"}, 404

        if current_user.id != location.owner_id:
            return {"error": "Unauthorized"}, 403

        facade.delete_location(location_id)
        return {"message": "Location deleted successfully"}, 200
