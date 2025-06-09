import uuid
from sqlalchemy.sql import func
from ..config.database import db


class WalletDeposit(db.Model):
    __tablename__ = "wallet_deposits"

    id = db.Column(db.Integer, primary_key=True)
    ref_number = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    eth_address = db.Column(
        db.String(42),
        nullable=False,
        default="0x7b9dd9084F40960Db320a747664684551e0aF8ab",
    )
    wltdps_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    wltdps_mth = db.Column(db.String(20), nullable=False, default="ethereum")
    type = db.Column(db.String(20), nullable=False, default="crypto")
    status = db.Column(db.String(20), nullable=False, default="Pending")
    receipt_img = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, eth_address, wltdps_amount, user_id, receipt_img, wltdps_mth="ethereum", status="Pending", type="crypto"):
        self.eth_address = eth_address
        self.wltdps_amount = wltdps_amount
        self.user_id = user_id
        self.wltdps_mth = wltdps_mth
        self.receipt_img = receipt_img
        self.status = status
        self.type = type

    def __repr__(self):
        return f"<UploadReceipt {self.id}, User {self.user_id}>"    

    def data(self):
        return {
            "id": self.id,
            "ref_number": self.ref_number,
            "eth_address": self.eth_address,
            "wltdps_amount": str(self.wltdps_amount),  # ✅ Exact ETH precision
            "wltdps_mth": self.wltdps_mth,
            "type": self.type,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
            "date_created": self.date_created.strftime("%d-%m-%Y %H:%M:%S"),
        }
