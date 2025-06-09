import uuid
from sqlalchemy.sql import func
from ..config.database import db
import enum


# ✅ Define withdrawal methods
class WithdrawalMethod(enum.Enum):
    ethereum = "Ethereum"


class Withdrawal(db.Model):
    __tablename__ = "withdrawals"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Link to User
    eth_address = db.Column(db.String(42), nullable=False)  # Ethereum wallet address
    eth_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)  # Amount in ETH
    withdrawal_mth = db.Column(db.Enum(WithdrawalMethod), nullable=False, default=WithdrawalMethod.ethereum)  # Default to Ethereum
    status = db.Column(db.String(20), nullable=False, default="Pending")
    type = db.Column(db.String(20), nullable=True, default="crypto")  # Transaction type (optional)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())  # Timestamp
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())  # Created timestamp

    def __init__(
        self,
        eth_address,
        eth_amount,
        user_id,
        withdrawal_mth=WithdrawalMethod.ethereum,
        status="Pending",
        type="crypto",
    ):
        self.eth_address = eth_address
        self.eth_amount = eth_amount
        self.withdrawal_mth = withdrawal_mth
        self.user_id = user_id
        self.status = status
        self.type = type

    def data(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "eth_address": self.eth_address,
            "eth_amount": str(self.eth_amount),  # ✅ Prevents rounding issues
            "withdrawal_mth": self.withdrawal_mth.value,  # ✅ Access Enum value
            "status": self.status,  # ✅ Access Enum value
            "type": self.type,
            "timestamp": self.timestamp.strftime(
                "%d-%m-%Y %H:%M:%S"
            ),  # ✅ Format timestamp
            "date_created": self.date_created.strftime(
                "%d-%m-%Y %H:%M:%S"
            ),  # ✅ Consistent format
        }
