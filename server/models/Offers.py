from sqlalchemy.sql import func
from ..config.database import db


class Offers(db.Model):
    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    nft_image = db.Column(db.String(255), nullable=False)
    nft_name = db.Column(db.String(100), nullable=False)
    offered_price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)  # ✅ Prevent rounding
    buyer = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(20), nullable=False, default="Pending")
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, nft_image, nft_name, offered_price, buyer, user_id, action="Pending"):
        self.nft_image = nft_image
        self.nft_name = nft_name
        self.offered_price = offered_price
        self.buyer = buyer
        self.user_id = user_id
        self.action = action

    def data(self):
        return {
            "id": self.id,
            "nft_image": self.nft_image,
            "nft_name": self.nft_name,
            "offered_price": str(self.offered_price),  # ✅ No rounding errors
            "buyer": self.buyer,
            "action": self.action,
            "timestamp": self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
            "user_id": self.user_id,
            "date_created": self.date_created.strftime("%d-%m-%Y %H:%M:%S"),
        }