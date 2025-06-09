import uuid  # ✅ Import UUID for generating unique reference numbers
from sqlalchemy import func
from ..config.database import db
from ..models.enums import NFTStatus
from flask_login import current_user  # ✅ Import current_user to track logged-in user


class NFT(db.Model):
    __tablename__ = "nfts"

    id = db.Column(db.Integer, primary_key=True)
    ref_number = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    nft_name = db.Column(db.String(100), nullable=False)
    nft_image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    collection_name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    description = db.Column(db.Text, nullable=True)
    royalties = db.Column(
        db.Numeric(precision=5, scale=2), nullable=False, default=0.00
    )
    views = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False, default=NFTStatus.LISTED.value)
    creator = db.Column(db.String(100), nullable=False)
    buyer = db.Column(db.String(100), nullable=True)
    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", name="fk_nft_buyer_id"
        ),  # ✅ Explicitly name the foreign key constraint
        nullable=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", name="fk_nft_user"
        ),  # ✅ Explicitly name the constraint
        nullable=False,
    )
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    def increment_views(self):
        """Increase NFT view count."""
        self.views += 1
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "nft_name": self.nft_name,
            "nft_image": self.nft_image,
            "category": self.category,
            "price": str(
                self.price
            ),  # ✅ Convert price to string for JSON compatibility
            "status": self.status,
            "ref_number": self.ref_number,
            "buyer": self.buyer,
        }

    def data(self):
        """✅ Dynamically adjust status based on the viewer"""
        if current_user.is_authenticated and self.buyer_id == current_user.id:
            display_status = NFTStatus.SOLD.value
        else:
            display_status = NFTStatus.AVAILABLE.value

        return {
            "id": self.id,
            "ref_number": self.ref_number,
            "nft_name": self.nft_name,
            "nft_image": self.nft_image,
            "category": self.category,
            "collection_name": self.collection_name,
            "price": str(self.price),
            "description": self.description,
            "royalties": str(self.royalties),
            "views": self.views,
            "status": display_status,  # ✅ Dynamically adjusts based on user
            "creator": self.creator,
            "buyer_id": self.buyer_id,  # ✅ Track buyer in data response
            "user_id": self.user_id,
            "timestamp": self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
        }
