import uuid
from sqlalchemy import func
from ..models.enums import NFTStatus
from ..models.User import User
from ..config.database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    ref_number = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE", name="fk_transaction_user"),  # ✅ Explicitly name the constraint
        nullable=False,
    )
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)  # ✅ Add this field
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # ✅ Tracks NFT creator (owner) ID
    owner_name = db.Column(db.String(100), nullable=False)  # ✅ Add owner_name
    nft_id = db.Column(db.Integer, db.ForeignKey("nfts.id"), nullable=False)
    nft_ref_number = db.Column(db.String(36), nullable=False)
    eth_address = db.Column(db.String(42), nullable=False)
    listed_price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    receipt_img = db.Column(db.String(255), nullable=False)
    status = db.Column(
            db.Enum(NFTStatus), nullable=False, default=NFTStatus.PENDING
        )  # ✅ Use Enum
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    # ✅ Relationship to dynamically fetch latest user info
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    owner = db.relationship("User", foreign_keys=[owner_id])
    nft = db.relationship("NFT", foreign_keys=[nft_id])

    def __repr__(self):
        return (
            f"<Transaction {self.id}, Buyer {self.buyer.name}, Owner {self.owner.name}>"
        )

    @staticmethod
    def create_transaction(nft, buyer):
        """Creates a new transaction, linking owner dynamically from NFT.creator."""
        owner = User.query.get(nft.user_id)  # ✅ Get latest creator name using user_id
        if not owner:
            raise ValueError(f"Creator for NFT {nft.id} not found in Users table.")

        transaction = Transaction(
            buyer_id=buyer.id,
            buyer_name=buyer.name,
            owner_id=owner.id,
            owner_name=owner.name,  # ✅ Always stores the latest name from User table
            nft_id=nft.id,
            nft_ref_number=nft.ref_number,
            eth_address=buyer.eth_address,
            listed_price=nft.price,
            receipt_img="default_receipt.png",
            status="Pending",
        )

        db.session.add(transaction)
        db.session.commit()
        return transaction

    def data(self):
        return {
            "id": self.id,
            "ref_number": self.ref_number,
            "buyer_id": self.buyer_id,
            "buyer_name": self.buyer_name,  # ✅ Easier lookup by name
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,  # ✅ Easier lookup by name
            "nft_id": self.nft_id,
            "receipt_img": self.receipt_img,
            "nft_ref_number": self.nft_ref_number,
            "listed_price": str(self.listed_price),
            "status": self.status,
            "timestamp": self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
        }
