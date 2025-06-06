import uuid  # ✅ Import UUID for generating unique reference numbers
from sqlalchemy import func
from ..config.database import db
from ..models.enums import NFTStatus


class PendingNFTs(db.Model):
    __tablename__ = "pending_nfts"

    id = db.Column(db.Integer, primary_key=True)
    nft_name = db.Column(db.String(100), nullable=False)
    nft_image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    collection_name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    description = db.Column(db.Text, nullable=True)
    royalties = db.Column(
        db.Numeric(precision=5, scale=2), nullable=False, default=0.00
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    creator = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.Enum(NFTStatus), nullable=False, default=NFTStatus.PENDING
    )  # ✅ Use Enum
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
