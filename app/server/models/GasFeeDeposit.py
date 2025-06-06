from sqlalchemy.sql import func
from ..config.database import db


class GasFeeDeposit(db.Model):
    __tablename__ = "gas_fee_deposits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    eth_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    receipt_img = db.Column(db.String(255), nullable=False)  # Image file path
    status = db.Column(db.String(20), nullable=False, default="Pending")
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, eth_amount, receipt_img, user_id, status="Pending"):
        self.eth_amount = eth_amount
        self.user_id = user_id
        self.receipt_img = receipt_img
        self.status = status

    def __repr__(self):
        return f"<GasfeeDeposit {self.id}, User {self.user_id}>"

    def update_status(self, new_status):
        """Safely update deposit status"""
        valid_statuses = {"Pending", "Approved", "Rejected"}

        if new_status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{new_status}'. Must be one of {valid_statuses}"
            )

        self.status = new_status
        db.session.commit()  # ✅ Ensures safe commit within the model itself

    def data(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "eth_amount": str(self.eth_amount),  # ✅ Exact precision
            "receipt_img": self.receipt_img,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
            "date_created": self.date_created.strftime("%d-%m-%Y %H:%M:%S"),
        }
