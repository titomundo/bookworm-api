from flask_jwt_extended import get_jwt
from flask_jwt_extended.view_decorators import jwt_required
from flask_restx import Namespace, Resource, fields

from app.services import facade

api = Namespace("users", description="User operations")

user_model = api.model(
    "User",
    {
        "first_name": fields.String(
            required=True, description="First name of the user"
        ),
        "last_name": fields.String(required=True, description="Last name of the user"),
        "email": fields.String(required=True, description="Email of the user"),
        "password": fields.String(required=True, description="User Password"),
    },
)


@api.route("/profile")
class UserProfile(Resource):
    pass


@api.route("/")
class UserList(Resource):
    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, "User successfully created")
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def post(self):
        """Register a new user"""
        user_data = api.payload
        current_user = get_jwt()

        if not current_user.get("is_admin"):
            return {"error": "Admin privileges required"}, 403

        try:
            new_user = facade.create_user(user_data)
        except ValueError as e:
            return {"error": str(e)}, 400

        return new_user.as_dict(), 201

    @api.response(200, "List of users")
    def get(self):
        """Get a list of all users"""
        users = [u.as_dict() for u in facade.get_all_users()]
        return users, 200


@api.route("/<user_id>")
class UserResource(Resource):
    @api.response(200, "User details retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)

        if not user:
            return {"error": "User not found"}, 404

        return user.as_dict(), 200

    @jwt_required()
    @api.expect(user_model)
    @api.response(200, "User updated successfully")
    @api.response(404, "User not found")
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    def put(self, user_id):
        """Update an existing user"""
        user_data = api.payload
        email = user_data.get("email")
        current_user = get_jwt()

        if not current_user.get("is_admin"):
            return {"error": "Admin privileges required"}, 403

        if email:
            # Check if email is already in use
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {"error": "Email is already in use"}, 400

        try:
            user = facade.update_user(user_id, user_data)
        except ValueError as e:
            return {"error": str(e)}, 400

        if not user:
            return {"error": "User not found"}, 404

        return {"message": "User updated successfully"}, 200


@api.route("/<user_id>/businesses")
class UserBusinessList(Resource):
    @api.response(200, "List of businesses by user")
    @api.response(404, "User not found")
    def get(self, user_id):
        pass
