from flask_jwt_extended import current_user, get_jwt, get_jwt_identity
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
    @jwt_required()
    @api.response(200, "User profile")
    @api.response(404, "User not found")
    def get(self):
        user = facade.get_user(get_jwt_identity())

        if not user:
            return {"error": "user not found"}, 404

        return user.as_dict(), 200


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
        except (ValueError, TypeError) as e:
            return {"error": str(e)}, 400

        return new_user.as_dict(), 201

    @jwt_required()
    @api.response(200, "List of users")
    @api.response(403, "Admin privileges required")
    def get(self):
        """Get a list of all users"""
        user = facade.get_user(get_jwt_identity())

        if not user or user.role_name() != "Admin":
            return {"error": "Admin privileges required"}, 403

        users = [u.as_dict() for u in facade.get_all_users()]
        return users, 200


@api.route("/<user_id>")
class UserResource(Resource):
    @jwt_required()
    @api.response(200, "User details retrieved successfully")
    @api.response(403, "Admin privileges required")
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        current_user = facade.get_user(get_jwt_identity())

        if not current_user or current_user.role_name() != "Admin":
            return {"error": "Admin privileges required"}, 403

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
        current_user = facade.get_user(get_jwt_identity())

        if not current_user or current_user.role_name() != "Admin":
            return {"error": "Admin privileges required"}, 403

        if email:
            # Check if email is already in use
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {"error": "Email is already in use"}, 400

        try:
            user = facade.update_user(user_id, user_data)
        except (ValueError, TypeError) as e:
            return {"error": str(e)}, 400

        if not user:
            return {"error": "User not found"}, 404

        return {"message": "User updated successfully"}, 200
