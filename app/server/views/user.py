from flask import (
    Blueprint,
    jsonify,
    render_template,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from ..utils.minting_fee_helper import calculate_minting_fee
from ..models.enums import NFTStatus
from ..models.PendingNfts import PendingNFTs
from sqlalchemy import text
from ..config.database import db
from server import UPLOAD_FOLDER
from ..models.GasFeeDeposit import GasFeeDeposit
from ..models.Ether import Ether
from ..models.NFT import NFT
from ..models.NFTViews import NFTViews
from ..models.Offers import Offers
from ..models.User import User
from ..models.Withdrawal import Withdrawal
from ..models.WalletDeposit import WalletDeposit
from ..models.Transaction import Transaction
from .forms import (
    FinalisingPurchaseForm,
    OfferForm,
    ProfileForm,
    WithdrawalForm,
    WalletDepositForm,
    GasFeeDepositForm,
    CreateNftForm,
)
from email_validator import validate_email, EmailNotValidError
import os
import uuid
from werkzeug.utils import secure_filename
from decimal import Decimal
from server import csrf  # ✅ Ensure CSRF is imported from __init__.py


user = Blueprint("user", __name__)


# BUY PAGE ROUTE (VIEW)
@csrf.exempt
@user.route("/nft/buy/nft_<ref_number>", methods=["GET", "POST"])
@login_required
def buy_page(ref_number):
    try:
        uuid.UUID(ref_number, version=4)  # ✅ Validate reference number format
    except ValueError:
        flash("Invalid NFT reference number format.", "error")
        return redirect(url_for("user.dashboard_page"))

    nft = NFT.query.filter_by(ref_number=ref_number).first()

    if not nft:
        flash("NFT not found.", "error")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Log NFT view (tracking purposes)
    NFTViews.log_view(nft.id, current_user.id)

    ether = Ether.query.filter_by(user_id=current_user.id).first()
    user_balance = ether.main_wallet_balance if ether else 0.0000

    if request.method == "POST":
        # ✅ Check if the current user has already bought this NFT
        if nft.buyer_id == current_user.id:  # ✅ Ensure buyer ID matches user ID
            flash(f"You have already purchased '{nft.nft_name}'.", "error")
            return redirect(
                url_for("user.buy_page", ref_number=ref_number)
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


# FINALISING BUY PAGE ROUTE (VIEW)
@user.route("/finalising_purchase/nft_<ref_number>", methods=["GET", "POST"])
@login_required
def finalising_purchase(ref_number):
    try:
        uuid.UUID(ref_number, version=4)  # Validate reference number format
    except ValueError:
        flash("Invalid NFT reference number format.", "error")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Fetch NFT securely
    nft = NFT.query.filter_by(ref_number=ref_number).first()

    if not nft:
        flash("NFT not found.", "error")
        return redirect(url_for("user.buy_page", ref_number=ref_number))

    # ✅ Fetch NFT owner's details
    owner = User.query.filter_by(name=nft.creator).first()
    if not owner:
        flash("NFT creator not found.", "error")
        return redirect(url_for("user.buy_page", ref_number=ref_number))

    # ✅ Fetch user's wallet balance
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    user_balance = ether.main_wallet_balance if ether else 0.0000

    form = FinalisingPurchaseForm(obj=nft)
    form.listed_price.data = nft.price

    if request.method == "POST" and form.validate_on_submit():
        eth_address = form.eth_address.data
        listed_price = nft.price
        receipt_img = request.files.get("receipt_img")

        if user_balance < nft.price:
            flash(
                f"Insufficient funds! NFT costs {nft.price} ETH, but you have {user_balance} ETH.",
                "error",
            )
            return redirect(url_for("user.buy_page", ref_number=ref_number))

        def allowed_file(filename):
            return "." in filename and filename.rsplit(".", 1)[1].lower() in {
                "png",
                "jpg",
                "jpeg",
                "webp",
            }

        if not receipt_img or not allowed_file(receipt_img.filename):
            flash(
                "Invalid file type! Only PNG, JPG, JPEG, and WEBP are allowed.", "error"
            )
            return redirect(url_for("user.finalising_purchase", ref_number=ref_number))

        filename = secure_filename(receipt_img.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            receipt_img.save(save_path)

            # ✅ Create a transaction with Owner & Buyer info
            transaction = Transaction(
                user_id=current_user.id,  # ✅ Ensures the required user_id is set
                buyer_id=current_user.id,
                buyer_name=current_user.name,
                owner_id=owner.id,
                owner_name=owner.name,
                nft_id=nft.id,
                nft_ref_number=nft.ref_number,
                eth_address=eth_address,
                listed_price=listed_price,
                receipt_img=unique_filename,
                status=NFTStatus.PENDING,
            )

            db.session.add(transaction)
            db.session.commit()

            flash(
                "Purchase request was successful! Kindly wait for approval of your request.",
                "success",
            )
            return redirect(url_for("user.dashboard_page"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during the transaction: {str(e)}", "danger")
            print(f"An error occurred during the transaction: {str(e)}")
            return redirect(url_for("user.buy_page", ref_number=ref_number))

    return render_template(
        "main/pages/finalising-purchase-page.html",
        title=f"Buy {nft.nft_name} | MintVerse",
        current_user=current_user,
        nft=nft,
        user_balance=user_balance,
        ref_number=ref_number,
        form=form,
    )


# DASHBOARD EXPLORE PAGE ROUTE (VIEW)
@user.get("/dashboard")
@login_required
def dashboard_page():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("mintverse.home_page"))

    # Get the user's wallet balance from Ether model
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.main_wallet_balance if ether else 0.0000

    return render_template(
        "main/pages/user/dashboard.html",
        title="Dashboard | MintVerse",
        name=current_user.name,
        eth_count=eth_count,
        current_user=current_user,
    )


# OFFER PAGE ROUTE (VIEW)
@user.route("/offers", methods=["GET", "POST"])
@login_required
def offers_page():

    # ✅ Fetch the logged-in user's ETH balance
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.main_wallet_balance if ether else 0.0000
   
    # ✅ Fetch all offers for the logged-in user, including approved & rejected ones
    offers = Offers.query.filter_by(user_id=current_user.id).order_by(Offers.timestamp.desc()).all()

    return render_template(
        "main/pages/user/offers-page.html",
        title="Your Offers | MintVerse",
        name=current_user.name,
        eth_count=eth_count,
        offers=offers,  # ✅ Pass pending offers to the template
        current_user=current_user,
    )


# OFFER PAGE ROUTE (VIEW)
@user.route("/finalise_offer/nft_<ref_number>", methods=["GET", "POST"])
@login_required
def finalise_offer_page(ref_number):
    # ✅ Validate UUID format for reference number
    try:
        uuid.UUID(ref_number, version=4)  # Ensure it's a valid UUID
    except ValueError:
        flash("Invalid NFT reference number format.", "error")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Fetch NFT securely from the database
    nft = NFT.query.filter_by(ref_number=ref_number).first()

    # ✅ Handle NFT not found
    if not nft:
        flash("NFT not found.", "error")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Fetch the logged-in user's ETH balance
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.main_wallet_balance if ether else 0.0000

    form = OfferForm()

    # ✅ Handle Offer Submission (POST request)
    if request.method == "POST" and form.validate_on_submit():
        nft_image = nft.nft_image  # ✅ NFT Image
        nft_name = nft.nft_name  # ✅ NFT Name
        offered_price = form.offered_price.data  # ✅ Offered price in ETH
        buyer = current_user.name  # ✅ Automatically assign buyer name

        # ✅ Determine minimum allowed price based on NFT price range
        if nft.price >= Decimal("2.0000"):
            min_allowed_price = max(nft.price - Decimal("1.0000"), Decimal("0.001"))  # ✅ Ensure minimum price is never below 0.001 ETH
        else:
            min_allowed_price = max(nft.price - Decimal("0.0200"), Decimal("0.001"))  # ✅ Adjust threshold for NFTs priced ≤ 1.9999 ETH

        # ✅ Maximum price remains the NFT price itself
        max_allowed_price = nft.price

        # ✅ Validate if offered_price is within the acceptable range
        if not (min_allowed_price <= offered_price <= max_allowed_price):
            flash(
                f"Invalid offer! Your offer must be between {min_allowed_price:.4f} ETH and {max_allowed_price:.4f} ETH.",
                "error",
            )
            return redirect(url_for("user.finalise_offer_page", ref_number=ref_number))
        # ✅ Ensure the user has sufficient ETH balance
        if eth_count < offered_price:
            flash(
                f"Insufficient funds! You have {eth_count} ETH but tried to offer {offered_price} ETH.",
                "error",
            )
            return redirect(url_for("user.buy_page"))

        try:
            # ✅ Create a new Offer entry
            offer = Offers(
                user_id=current_user.id,
                nft_image=nft_image,
                nft_name=nft_name,
                offered_price=offered_price,
                buyer=buyer,
                action="Pending",
            )
            db.session.add(offer)
            db.session.commit()
            flash(
                f"Your offer of {offered_price} ETH on {nft_name} has been submitted successfully! Await approval.",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while submitting your offer: {str(e)}", "danger")

        return redirect(url_for("user.offers_page", ref_number=ref_number))

    # ✅ Fetch pending offers for the logged-in user
    offers = Offers.query.filter_by(user_id=current_user.id, action="Pending").all()

    return render_template(
        "main/pages/user/finalising-offers-page.html",
        title="Finalise Offers | MintVerse",
        name=current_user.name,
        ref_number=ref_number,
        eth_count=eth_count,
        nft=nft,
        offers=offers,  # ✅ Pass pending offers to the template
        current_user=current_user,
        form=form,  # ✅ Ensure the form is passed to the template
    )


# WALLET PAGE ROUTE (VIEW)
@user.get("/wallet")
@login_required
def wallet_page():
    name = current_user.name
    return render_template(
        "main/pages/user/wallet-page.html",
        title="User Wallet | MintVerse",
        name=name,
        current_user=current_user,
    )


# WALLET_DEPOSIT PAGE ROUTE (VIEW)
@user.route("/wallet/wallet_deposit", methods=["GET", "POST"])
@login_required
def wallet_deposit_page():
    form = WalletDepositForm()

    if request.method == "POST":
        # ✅ Validate form input
        if not form.validate_on_submit():
            flash("There were validation errors. Please check your inputs.", "danger")
            return redirect(url_for("user.wallet_deposit_page"))

        eth_address = form.eth_address.data
        wltdps_amount = form.wltdps_amount.data
        receipt_img = request.files.get("receipt_img")

        # ✅ Enforce minimum deposit limit
        if wltdps_amount < 0.001:
            flash("Invalid deposit amount. Minimum deposit is 0.001 ETH.", "danger")
            return redirect(url_for("user.wallet_deposit_page"))

        # ✅ Validate receipt file upload
        def allowed_file(filename):
            return "." in filename and filename.rsplit(".", 1)[1].lower() in {
                "png",
                "jpg",
                "jpeg",
                "webp",
            }

        if not receipt_img or not allowed_file(receipt_img.filename):
            flash(
                "Invalid file type! Only PNG, JPG, JPEG, and WEBP are allowed.", "error"
            )
            return redirect(url_for("user.wallet_deposit_page"))

        filename = secure_filename(receipt_img.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            # ✅ Ensure upload directory exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            receipt_img.save(save_path)  # ✅ Save file securely

            # ✅ Create Wallet Deposit Entry (ONLY marked as Pending)
            deposit = WalletDeposit(
                eth_address=eth_address,
                wltdps_amount=wltdps_amount,
                user_id=current_user.id,
                receipt_img=unique_filename,
                wltdps_mth="ethereum",
                status="Pending",  # ✅ Balance will only update on approval
                type="crypto",
            )
            db.session.add(deposit)
            db.session.commit()

            flash(
                f"Wallet deposit of {wltdps_amount} ETH submitted successfully. Patiently wait for approval!",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

            if os.path.exists(save_path):
                os.remove(save_path)

            flash(f"An error occurred while saving Receipt: {e}", "danger")

        return redirect(url_for("user.wallet_deposit_page"))

    # ✅ Fetch user's wallet balance
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.main_wallet_balance if ether else 0.0000

    # ✅ Fetch deposit history
    wltdps_hst = WalletDeposit.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "main/pages/user/wallet-deposit-page.html",
        title="Wallet Deposit | MintVerse",
        form=form,
        eth_count=eth_count,
        current_user=current_user,
        wltdps_hst=wltdps_hst,
    )


# GASFEE_DEPOSIT PAGE ROUTE (VIEW)
@user.route("/wallet/gasfee_deposit", methods=["GET", "POST"])
@login_required
def gasfee_deposit_page():
    gasfee_wallet_address = "0x7b9dd9084F40960Db320a747664684551e0aF8ab"
    form = GasFeeDepositForm()

    if request.method == "POST" and form.validate_on_submit():
        eth_amount = form.eth_amount.data
        receipt_img = request.files.get("receipt_img")

        # ✅ Validate minimum deposit amount
        if eth_amount < 0.001:
            flash("Invalid deposit amount. Minimum deposit is 0.001 ETH.", "danger")
            return redirect(url_for("user.gasfee_deposit_page"))

        # ✅ Validate receipt file upload
        def allowed_file(filename):
            return "." in filename and filename.rsplit(".", 1)[1].lower() in {
                "png",
                "jpg",
                "jpeg",
                "webp",
            }

        if not receipt_img or not allowed_file(receipt_img.filename):
            flash(
                "Invalid file type! Only PNG, JPG, JPEG, and WEBP are allowed.", "error"
            )
            return redirect(
                url_for("user.gasfee_deposit_page")
            )  # ✅ Fix redirect mismatch

        filename = secure_filename(receipt_img.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            # ✅ Ensure upload directory exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            receipt_img.save(save_path)  # ✅ Save file securely

            # ✅ Create Gas Fee Deposit Entry with unique reference
            gas_fee_deposit = GasFeeDeposit(
                eth_amount=eth_amount,
                user_id=current_user.id,
                receipt_img=unique_filename,
                status="Pending",
            )
            db.session.add(gas_fee_deposit)
            db.session.commit()

            flash(
                f"Gas fee deposit of {eth_amount} ETH submitted successfully! Kindly wait for approval.",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")

            if os.path.exists(save_path):
                os.remove(save_path)

            flash(f"An error occurred while saving the receipt: {e}", "danger")

        return redirect(url_for("user.gasfee_deposit_page"))

    # ✅ Fetch the user's gas fee balance (Ensure structured retrieval)
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    gasfee_count = ether.gas_fee_balance if ether else 0.0000

    return render_template(
        "main/pages/user/gasfee-deposit-page.html",
        title="Gas Fee Deposit | MintVerse",
        form=form,
        gasfee_wallet_address=gasfee_wallet_address,
        gasfee_count=gasfee_count,
        current_user=current_user,
    )


# WITHDRAWAL PAGE ROUTE (VIEW)
@user.route("/wallet/withdrawal", methods=["GET", "POST"])
@login_required
def withdrawal_page():
    form = WithdrawalForm()

    if request.method == "POST" and form.validate_on_submit():
        withdrawal_mth = form.withdrawal_mth.data

        # ✅ Ensure a valid method is selected
        if not withdrawal_mth:
            flash("Please select a valid withdrawal method.", "error")
            return redirect(url_for("user.withdrawal_page"))

        # ✅ Fetch withdrawal details
        eth_address = form.eth_address.data
        eth_amount = form.eth_amount.data

        # ✅ Fetch user's Ether wallet balance
        ether = Ether.query.filter_by(user_id=current_user.id).first()
        user_balance = ether.main_wallet_balance if ether else 0.0000

        if user_balance < eth_amount:
            flash(
                f"Insufficient balance! You need {eth_amount} ETH, but have {user_balance} ETH.",
                "error",
            )
            return redirect(url_for("user.withdrawal_page"))

        try:
            # ✅ Create withdrawal request (NO balance deduction yet)
            withdrawal = Withdrawal(
                eth_address=eth_address,
                eth_amount=eth_amount,
                withdrawal_mth=withdrawal_mth,
                user_id=current_user.id,
                status="Pending",  # ✅ Balance will only update upon approval
                type="crypto",
            )
            db.session.add(withdrawal)
            db.session.commit()

            flash(
                "Withdrawal request submitted successfully! Await admin approval.",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while processing withdrawal: {str(e)}", "danger")

        return redirect(url_for("user.withdrawal_page"))

    # ✅ Fetch user's withdrawal history
    wth_hst = Withdrawal.query.filter_by(user_id=current_user.id).all()

    # ✅ Fetch user's wallet balance
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.main_wallet_balance if ether else 0.0000

    return render_template(
        "main/pages/user/withdrawal-page.html",
        title="Withdrawal | MintVerse",
        form=form,
        eth_count=eth_count,
        current_user=current_user,
        wth_hst=wth_hst,  # ✅ Pass withdrawal history to the template
    )


# PROFILE PAGE ROUTE (VIEW)
@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("mintverse.home_page"))

    form_data = ProfileForm(obj=user)

    if request.method == "POST" and form_data.validate_on_submit():
        # Fetch form data
        name = form_data.name.data
        email = form_data.email.data
        dob = form_data.dob.data
        bio = form_data.bio.data
        address = form_data.address.data
        city = form_data.city.data
        state = form_data.state.data
        zipcode = form_data.zipcode.data
        country = form_data.country.data
        phone = form_data.phone.data
        gender = form_data.gender.data

        # Validate email format
        try:
            valid_email = validate_email(email)
            email = valid_email.normalized
        except EmailNotValidError as e:
            flash(f"Invalid email format: {e}", category="error")
            return redirect(url_for("user.profile_page"))

        # Check for duplicate email (ignore if unchanged)
        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("This email is already in use by another user.", "error")
                return redirect(url_for("user.profile_page"))

        # Update user details
        user.name = name
        user.email = email
        user.dob = dob
        user.bio = bio
        user.address = address
        user.city = city
        user.state = state
        user.zipcode = zipcode
        user.country = country
        user.phone = phone
        user.gender = gender

        try:
            db.session.commit()
            flash("Your profile has been updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating your profile: {e}", "danger")

        return redirect(url_for("user.profile_page"))

    return render_template(
        "main/pages/user/profile-page.html",
        title="Profile | MintVerse",
        form=form_data,
        current_user=current_user,
    )


# CREATE NFT PAGE ROUTE (VIEW)
@user.route("/nft/create_nft", methods=["GET", "POST"])
@login_required
def create_nft_page():
    form = CreateNftForm()
    form.creator.data = current_user.name

    # ✅ Fetch current minting fee dynamically
    minting_fee = calculate_minting_fee()
    if minting_fee is None:
        flash("Could not retrieve live minting fee. Try again later.", "error")
        return redirect(url_for("user.create_nft_page"))

    if request.method == "POST" and form.validate_on_submit():
        ether = Ether.query.filter_by(user_id=current_user.id).first()
        gas_fee_balance = ether.gas_fee_balance if ether else Decimal("0.0000")

        if gas_fee_balance < minting_fee:
            flash(
                f"Insufficient gas fee balance! Minting requires {minting_fee} ETH, but you have {gas_fee_balance} ETH.",
                "error",
            )
            return redirect(url_for("user.create_nft_page"))

        # ✅ Deduct minting fee dynamically
        ether.gas_fee_balance -= minting_fee
        db.session.commit()

        # ✅ NFT creation logic remains unchanged...

        # Extract form data
        nft_name = form.item_name.data
        category = form.category.data
        collection_name = form.collection_name.data
        creator = current_user.name
        price = form.list_price.data
        royalties = form.royalties.data
        description = form.item_des.data

        # Handle file upload
        nft_logo = request.files.get("nft_logo")
        if not nft_logo or nft_logo.filename == "":
            flash("Please upload a valid NFT file!", "error")
            return redirect(url_for("user.create_nft_page"))

        filename = secure_filename(nft_logo.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            nft_logo.save(save_path)

            # ✅ Store in PendingNFTs (NOT the main NFT table)
            pending_nft = PendingNFTs(
                nft_name=nft_name,
                nft_image=f"/static/uploads/{unique_filename}",
                category=category,
                collection_name=collection_name,
                creator=creator,
                price=price,
                royalties=royalties,
                description=description,
                status=NFTStatus.PENDING,
                user_id=current_user.id,
            )
            db.session.add(pending_nft)
            db.session.commit()

            flash(
                "NFT sent for admin review. It will be added once approved!", "success"
            )
            return redirect(url_for("user.create_nft_page"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while saving NFT: {e}", "danger")

    # Fetch user's NFT collection & wallet balance
    nft_hst = (
        db.session.query(
            PendingNFTs.id,
            PendingNFTs.nft_name,
            PendingNFTs.nft_image,
            PendingNFTs.category,
            PendingNFTs.price,
            PendingNFTs.royalties,
            db.case((NFT.id.isnot(None), NFT.status), else_=PendingNFTs.status).label("status"), 
            PendingNFTs.user_id,
            db.case((NFT.id.isnot(None), NFT.timestamp), else_=PendingNFTs.timestamp).label("timestamp"), 
            db.case((NFT.id.isnot(None), NFT.ref_number), else_=db.literal(None)).label("ref_number"), 
            db.case((NFT.id.isnot(None), NFT.buyer), else_=db.literal(None)).label("buyer"),  # ✅ Updated Buyer Info
        )
        .outerjoin(NFT, NFT.nft_name == PendingNFTs.nft_name)
        .filter(PendingNFTs.user_id == current_user.id)
        .order_by(PendingNFTs.timestamp.desc())
        .all()
    )
    ether = Ether.query.filter_by(user_id=current_user.id).first()
    eth_count = ether.gas_fee_balance if ether else 0.0000

    return render_template(
        "main/pages/user/create-nft-page.html",
        title="Create NFT | MintVerse",
        form=form,
        eth_count=eth_count,
        nft_hst=nft_hst,
        current_user=current_user,
    )


# DELETE NFT RECORD
@user.route("/nft/delete_nft_record/<nft_id>", methods=["POST"])
@login_required
def delete_nft_record(nft_id):
    nft = PendingNFTs.query.filter_by(id=nft_id, user_id=current_user.id).first()

    if not nft:
        flash("NFT not found.", "error")
        return redirect(url_for("user.create_nft_page"))

    try:
        db.session.delete(nft)
        db.session.commit()
        flash(f"NFT record for '{nft.nft_name}' was deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting NFT: {str(e)}", "danger")

    return redirect(url_for("user.create_nft_page"))


# MY COLLECTIONS
@user.get("/mycollections/nfts")
@login_required
def mycollection_page():
    """✅ Renders the user's collections page"""
    return render_template(
        "main/pages/user/myCollection-page.html",
        title="My Collections | MintVerse",
        current_user=current_user,
    )


@user.get("/mycollection/listed/api/nfts/")
@login_required
def get_my_listed_collection():
    """✅ Fetches NFTs created by the logged-in user"""
    try:
        listed_nfts = NFT.query.filter(
            NFT.user_id == current_user.id, NFT.status == NFTStatus.AVAILABLE
        ).all()

        print(
            f"Retrieved {len(listed_nfts)} NFTs for user {current_user.name}"
        )  # ✅ Logs NFT count

        return jsonify([{
            "id": n.id,
            "ref_number": n.ref_number,
            "nft_name": n.nft_name,
            "nft_image": n.nft_image,
            "category": n.category,
            "price": str(n.price),  # ✅ String format for decimal values
            "status": n.status.value,  # ✅ Convert Enum to string
            "creator": n.creator,
        } for n in listed_nfts])

    except Exception as e:
        db.session.rollback()
        print(f"Error fetching listed NFTs: {e}")  # ✅ Logs errors properly
        return jsonify({"error": "Failed to fetch listed NFTs"}), 500


@user.get("/mycollection/bought/api/nfts/")
@login_required
def get_my_bought_collection():
    """✅ Fetches NFTs bought by the logged-in user"""
    try:
        bought_nfts = NFT.query.filter(
            NFT.buyer_id == current_user.id, NFT.status == NFTStatus.SOLD
        ).all()

        print(
            f"Retrieved {len(bought_nfts)} bought NFTs for user {current_user.name}"
        )  # ✅ Logs NFT count

        return jsonify([{
            "id": n.id,
            "ref_number": n.ref_number,
            "nft_name": n.nft_name,
            "nft_image": n.nft_image,
            "category": n.category,
            "price": str(n.price),  # ✅ String format for decimal values
            "status": n.status.value,  # ✅ Convert Enum to string
            "creator": n.creator,
        } for n in bought_nfts])

    except Exception as e:
        db.session.rollback()
        print(f"Error fetching bought NFTs: {e}")
        return jsonify({"error": "Failed to fetch bought NFTs"}), 500


@user.get("/nft/details/nft_<ref_number>")
@login_required
def nft_details(ref_number):
    try:
        nft = NFT.query.filter_by(ref_number=ref_number).first_or_404()

        transaction = Transaction.query.filter_by(
            nft_id=nft.id, status=NFTStatus.SOLD
        ).first()

        # ✅ Show "Sold" ONLY if current_user is the buyer
        display_status = (
            NFTStatus.SOLD
            if transaction and transaction.buyer_id == current_user.id
            else nft.status
        )

        buyer_name = transaction.buyer_name if transaction else None
        owner_name = transaction.owner_name if transaction else nft.creator

        return render_template(
            "main/pages/user/nft-details-page.html",
            title=f"{nft.nft_name} | MintVerse",
            nft=nft,
            display_status=display_status,
            owner_name=owner_name,
            buyer_name=buyer_name,
            current_user=current_user,
        )

    except Exception as e:
        print(f"Error fetching NFT details: {str(e)}")
        flash("Error loading NFT details. Please try again.", "error")
        return redirect(url_for("user.mycollection_page"))
