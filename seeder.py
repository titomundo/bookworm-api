from sqlalchemy.exc import IntegrityError

from app.services import facade
from run import app

roles = [
    {"name": "Admin", "description": "Super User"},
    {"name": "Owner", "description": "Business Owner"},
    {"name": "Employee", "description": "Regular User"},
]


with app.app_context():
    for role in roles:
        try:
            facade.create_role(role)
        except IntegrityError as e:
            print(e)

        role = facade.get_role_by_name("Admin")

        if not role:
            raise ValueError()

        admin_user = {
            "first_name": "Admin",
            "last_name": "Bookworm",
            "email": "admin@bookworm.io",
            "password": "bookwormadmin",
            "role_id": role.id,
        }

        try:
            facade.create_user(admin_user)
        except (ValueError, TypeError) as e:
            print(e)

    print(facade.get_all_roles())
    print(facade.get_all_users())
