from sqlalchemy.exc import IntegrityError

from app.services import facade
from run import app

# Creates all roles to start the application
# also adds some dummy users for testing and setup

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

    users = [
        {
            "first_name": "Admin",
            "last_name": "Bookworm",
            "email": "admin@bookworm.io",
            "password": "password",
            "role_id": facade.get_role_by_name("Admin").id,
        },
        {
            "first_name": "Owner",
            "last_name": "Bookworm",
            "email": "owner@bookworm.io",
            "password": "password",
            "role_id": facade.get_role_by_name("Owner").id,
        },
        {
            "first_name": "Employee",
            "last_name": "Bookworm",
            "email": "employee@bookworm.io",
            "password": "password",
            "role_id": facade.get_role_by_name("Employee").id,
        },
    ]

    for user in users:
        try:
            facade.create_user(user)
        except (ValueError, TypeError) as e:
            print(e)

    all_roles = facade.get_all_roles()
    all_users = facade.get_all_users()

    for role in all_roles:
        print(role)

    for user in all_users:
        print(user)
