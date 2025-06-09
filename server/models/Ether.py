from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from ..config.database import db  # Assuming this is your db instance


class Ether(db.Model):
    __tablename__ = "ethers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",  # ✅ Correct: Database handles cascade
            name="fk_ether_user",
        ),
        nullable=False,
    )
    main_wallet_balance = db.Column(
        db.Numeric(precision=10, scale=4), nullable=False, default=Decimal("0.0000")
    )
    gas_fee_balance = db.Column(
        db.Numeric(precision=10, scale=4), nullable=False, default=Decimal("0.0000")
    )
    last_updated = db.Column(
        db.DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    user = relationship(
        "User",
        backref=backref(
            "ether",  # This attribute will be added to the User model
            uselist=False,  # ✅ Key change: For one-to-one relationship (User.ether is a single object)
            cascade="all, delete-orphan",  # ORM-level cascade rules
            passive_deletes=True,  # Tells SQLAlchemy to let the DB handle cascade on delete
        ),
        lazy=True,
    )

    def __init__(self, user_id, main_wallet_balance=0.0000, gas_fee_balance=0.0000):
        self.user_id = user_id
        self.main_wallet_balance = Decimal(
            str(main_wallet_balance)
        )  # Ensure Decimal conversion
        self.gas_fee_balance = Decimal(
            str(gas_fee_balance)
        )  # Ensure Decimal conversion

    # ... (rest of your methods remain the same) ...

    def update_wallet_balance(self, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount < 0 and abs(amount) > self.main_wallet_balance:
            raise ValueError("Insufficient funds in main wallet")
        try:
            self.main_wallet_balance += amount
            # self.last_updated = func.now() # onupdate handles this if the record is flushed
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating wallet balance: {e}")

    def update_gas_fee_balance(self, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount < 0 and abs(amount) > self.gas_fee_balance:
            raise ValueError("Insufficient gas fee balance")
        try:
            self.gas_fee_balance += amount
            # self.last_updated = func.now() # onupdate handles this
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating gas fee balance: {e}")

    def set_wallet_balance(self, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        try:
            self.main_wallet_balance = amount
            # self.last_updated = func.now() # onupdate handles this
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error setting wallet balance: {e}")

    def set_gas_fee_balance(self, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount < 0:
            raise ValueError("Gas fee balance cannot be negative")
        try:
            self.gas_fee_balance = amount
            # self.last_updated = func.now() # onupdate handles this
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error setting gas fee balance: {e}")

    def data(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "main_wallet_balance": str(self.main_wallet_balance),
            "gas_fee_balance": str(self.gas_fee_balance),
            "last_updated": (
                self.last_updated.strftime("%d-%m-%Y %H:%M:%S")
                if self.last_updated
                else None
            ),
        }
