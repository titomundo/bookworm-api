from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restx import Namespace, Resource, fields

from app.services import facade

api = Namespace("businesses", description="Business operations")

business_model = api.model(
    "Business",
    {
        "name": fields.String(required=True, descripion="Name of the businesses"),
        "description": fields.String(required=False, description="Description"),
        "email": fields.String(required=True, description="Business email"),
        "phone_number": fields.String(
            required=True, description="Business phone number"
        ),
    },
)


@api.route("/")
class BusinessList(Resource):
    @jwt_required()
    @api.expect(business_model, validate=True)
    @api.response(201, "Business successfully created")
    @api.response(400, "Invalid input data")
    @api.response(403, "Unauthorized")
    def post(self):
        """Create new business"""
        business_data = api.payload
        current_user = facade.get_user(get_jwt_identity())

        if not current_user:
            return {"error": "user not found"}, 404

        if not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        try:
            business_data["owner_id"] = current_user.id
            new_business = facade.create_business(business_data)
        except ValueError as e:
            return {"error": str(e)}, 400

        return new_business.as_dict(), 201

    @api.response(200, "List of businesses")
    @api.response(403, "Invalid credentials")
    @jwt_required()
    def get(self):
        """Get list of all businesses for the current user"""
        current_user = facade.get_user(get_jwt_identity())

        if not current_user:
            return {"error": "invalid credentials"}, 403

        businesses = [b.as_dict() for b in current_user.businesses]
        return businesses, 200

@api.route("/<business_id>")
class BusinessResource(Resource):
    @jwt_required()
    @api.response(200, "Business deleted successfully")
    @api.response(404, "Business not found")
    @api.response(403, "Unauthorized")
    def delete(self, business_id):
        """Delete a business"""
        business = facade.get_business(business_id)
        current_user = facade.get_user(get_jwt_identity())

        if not current_user:
            return {"error": "invalid credentials"}, 403

        if not business:
            return {"error": "business not found"}, 404

        facade.delete_business(business_id)
        return {"message": "Business deleted successfully"}, 200
