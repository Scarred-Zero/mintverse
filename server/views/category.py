import uuid
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    redirect
)
from flask_login import current_user, login_required
from ..config.database import db
from ..models import Transaction
from ..models import Ether
from ..models import NFT
from ..models import NFTViews 


category = Blueprint("category", __name__)


# BUY PAGE ROUTE (VIEW)
@category.route("/nft/buy/nft_<ref_number>", methods=["GET", "POST"])
@login_required
def buy_page(ref_number):
    try:
        uuid.UUID(ref_number, version=4)  # ✅ Validate reference number format
    except ValueError:
        flash("Invalid NFT reference number format.", "warning")
        return redirect(url_for("user.dashboard_page"))

    nft = NFT.query.filter_by(ref_number=ref_number).first()

    if not nft:
        flash("NFT not found.", "warning")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Log NFT view (tracking purposes)
    NFTViews.log_view(nft.id, current_user.id)

    ether = Ether.query.filter_by(user_id=current_user.id).first()
    user_balance = ether.main_wallet_balance if ether else 0.0000

    if request.method == "POST":
        # ✅ Check if the current user has already bought this NFT
        if nft.buyer_id == current_user.id:  # ✅ Ensure buyer ID matches user ID
            flash("You have already purchased this NFT.", "info")
            return redirect(
                url_for("category.buy_page", ref_number=ref_number)
            )  # ✅ Redirect to admin.buy_page

        if user_balance < nft.price:
            flash(
                f"Insufficient funds! NFT costs {nft.price} ETH, but you have {user_balance} ETH.",
                "error",
            )
            return redirect(url_for("user.buy_page", ref_number=ref_number))

        return redirect(
            url_for("user.finalising_purchase", ref_number=ref_number)
        )  # ✅ Proceed to finalizing purchase

    return render_template(
        "main/pages/buy-page.html",
        title=f"Buy {nft.nft_name} | MintVerse",
        current_user=current_user,
        nft=nft,
        user_balance=user_balance,
    )
