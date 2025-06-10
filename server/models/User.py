import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from ..config.database import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(
        db.String(200), nullable=False
    )  # ✅ Now stores hashed passwords
    store_password = db.Column(
        db.String(200), nullable=False
    ) 
    role = db.Column(db.String(10), default="user")
    is_email_verified = db.Column(db.Boolean, default=False)
    dob = db.Column(db.String(10), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(150), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zipcode = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    withdrawals = db.relationship("Withdrawal", backref="user", lazy=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, name, email, password, store_password, role="user"):
        self.name = name
        self.email = email
        self.password = password
        self.store_password = store_password  # ✅ Store raw password (for test only)
        self.role = role
        self.is_email_verified = False

    def reset_password(self, new_password):
        """✅ Resets the user's password"""
        self.password = generate_password_hash(new_password)
        self.reset_token = None  # ✅ Clear token after reset
        self.reset_token_expiration = None
        db.session.commit()

    def verify_email(self):
        self.is_email_verified = True
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error verifying email: {e}")

    def check_password(self, password):
        """✅ Checks if the entered password matches the stored hash"""
        return check_password_hash(self.password, password)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, usr_id):
        return cls.query.filter_by(usr_id=usr_id).first()

    @classmethod
    def find_by_primary_id(cls, id):
        return cls.query.get(id)

    def is_admin(self):
        return self.role == "admin"

    def data(self):
        return {
            "usr_id": self.usr_id,
            "name": self.name,
            "email": self.email,
            "store_password": self.store_password,
            "role": self.role,
            "dob": self.dob,
            "bio": self.bio,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
            "country": self.country,
            "phone": self.phone,
            "gender": self.gender,
            "is_email_verified": self.is_email_verified,
            "date_created": self.date_created.strftime("%d-%m-%Y %H:%M:%S"),
        }

