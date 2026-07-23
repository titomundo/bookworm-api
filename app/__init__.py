import re

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()


def is_valid_email(email):
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"

    if not re.match(regex, email) or not email.strip():
        return False

    return True


def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    api = Api(
        app,
        version="1.0",
        title="Bookworm",
        description="Bookworm API",
        doc="/api/v1/",
    )

    CORS(app)

    # Move imports down here to prevent circular import errors
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.businesses import api as businesses_ns
    from app.api.v1.users import api as users_ns
    from app.api.v1.locations import api as locations_ns

    # Placeholder for API namespaces (endpoints will be added later)
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(businesses_ns, path="/api/v1/businesses")
    api.add_namespace(locations_ns, path="/api/v1/locations")
    api.add_namespace(auth_ns, path="/api/v1/auth")

    return app
