# import os
from werkzeug.security import generate_password_hash
from ..models.User import User  # ✅ Import your User model
from ..config.database import db  # ✅ Import your database instance
from ..config.variables import ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD


def create_admin_on_startup():
    """✅ Ensures an admin user exists in the database."""
    try:
        # ✅ Check if an admin user already exists
        admin_user = User.query.filter_by(role="admin").first()

        store_password = ADMIN_PASSWORD

        if not admin_user:
            # ✅ Create a new admin user
            new_admin = User(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                password=generate_password_hash(ADMIN_PASSWORD),  # ✅ Hash password
                role="admin",
                store_password=store_password,
                # is_email_verified=True,  # ✅ Ensure admin email is verified
            )

            db.session.add(new_admin)
            db.session.commit()

            print("Admin user created successfully:", ADMIN_EMAIL)
        else:
            print("Admin user already exists.")

    except Exception as e:
        db.session.rollback()
        print("Error creating admin user:", str(e))
