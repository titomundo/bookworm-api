import datetime
from os import access

from flask import jsonify, make_response
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields

from app.services import facade

api = Namespace("auth", description="Authentication operations")

login_model = api.model(
    "Login",
    {
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
)

register_model = api.model(
    "Register",
    {
        "first_name": fields.String(required=True, description="User first name"),
        "last_name": fields.String(required=True, description="User last name"),
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
)


@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, "Login successful")
    @api.response(401, "Invalid credentials")
    def post(self):
        """
        Authenticate user and return a JWT token

        TODO: implement login as cookie when using https
        """
        credentials = api.payload
        user = facade.get_user_by_email(credentials.get("email"))

        if not user or not user.verify_password(credentials.get("password")):
            return {"error": "Invalid credentials"}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role_name()},
            expires_delta=datetime.timedelta(days=1),
        )

        return {"access_token": access_token}, 200


@api.route("/register")
class Register(Resource):
    @api.expect(register_model, validate=True)
    @api.response(201, "User registered successfully")
    @api.response(400, "Invalid credentials")
    def post(self):
        """Register new user as an admin"""
        user_data = api.payload
        email = user_data.get("email")

        if facade.get_user_by_email(email):
            return {"error": "Email already registered"}, 400

        role = facade.get_role_by_name("Owner")

        if not role:
            return {"error", "Role not found"}, 400

        try:
            user_data["role_id"] = role.id
            new_user = facade.create_user(user_data)
        except ValueError as e:
            return {"error": str(e)}, 400

        access_token = create_access_token(
            identity=str(new_user.id),
            additional_claims={"role": new_user.role_name()},
            expires_delta=datetime.timedelta(days=1),
        )

        return {"access_token": access_token}, 200
