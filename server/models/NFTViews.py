from sqlalchemy import func
from ..config.database import db
from ..models import NFT

class NFTViews(db.Model):
    __tablename__ = "nft_views"

    id = db.Column(db.Integer, primary_key=True)
    nft_id = db.Column(db.Integer, db.ForeignKey("nfts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True), default=func.now()
    )  # ✅ Track view time

    @staticmethod
    def has_user_viewed(nft_id, user_id):
        """Check if a user has already viewed a specific NFT."""
        return (
            db.session.query(NFTViews).filter_by(nft_id=nft_id, user_id=user_id).first()
            is not None
        )

    @staticmethod
    def log_view(nft_id, user_id):
        """Log a new view if the user hasn't seen the NFT before."""
        if not NFTViews.has_user_viewed(nft_id, user_id):  # ✅ Corrected reference
            new_view = NFTViews(nft_id=nft_id, user_id=user_id)
            db.session.add(new_view)
            db.session.commit()

            nft = NFT.query.get(nft_id)
            if nft:
                nft.views += 1
                db.session.commit()
