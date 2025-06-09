from decimal import Decimal
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, render_template, redirect, flash, url_for
from flask_login import login_required, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.minting_fee_helper import calculate_minting_fee
from ..models.enums import NFTStatus
from ..models.PendingNfts import PendingNFTs
from server import UPLOAD_FOLDER
from ..config.database import db
from sqlalchemy import or_
from ..models.NFT import NFT
from ..models.Offers import Offers
from ..models.Withdrawal import Withdrawal
from ..models.Transaction import Transaction
from ..models.GasFeeDeposit import GasFeeDeposit
from ..models.Ether import Ether
from ..models.WalletDeposit import WalletDeposit
from ..models.Contact import Contact
from ..models.User import User
from ..utils.decorators import admin_required
from ..utils.helpers import validate_password
from .forms import (
    AdminAddNftForm,
    AdminCreationForm,
    AdminEditNftDetails,
    AdminLoginForm,
    AddUserForm,
    SearchForm,
    AdminEditUserProfileForm,
)
import os
import uuid
from werkzeug.utils import secure_filename
from server import csrf  # ✅ Ensure CSRF is imported from __init__.py


admin = Blueprint("admin", __name__)


@admin.route("/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    search_form = SearchForm()
    user = User.query.filter_by(id=current_user.id).first()

    if user.role != "admin" and user.id != 1:
        flash("You do not have permission to access that page.", category="danger")
        return redirect(url_for("mintverse.home_page"))

    # ✅ Get total counts for dashboard metrics
    user_count = User.query.count()
    contact_msg = Contact.query.count()
    wallet_deposit_count = WalletDeposit.query.count()  # ✅ Count wallet deposits
    transaction_count = Transaction.query.count()  # ✅ Count transactions

    if not current_user.is_admin():
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("user.dashboard_page"))

    return render_template(
        "admin/admin-dashboard.html",
        title="Admin Dashboard",
        current_user=current_user,
        user_count=user_count,
        contact_msg=contact_msg,
        wallet_deposit_count=wallet_deposit_count,  # ✅ Pass to frontend
        transaction_count=transaction_count,  # ✅ Pass to frontend
        search_form=search_form,
    )


# HANDLE ROUTE FOR ADMIN_PAGE
@admin.get("/admin_profile")
@login_required
def admin_profile():
    search_form = SearchForm()
    user = User.query.filter_by(id=current_user.id).first()
    if user.role != "admin" and user.id != 1:
        flash("You do not have permission to access that page.", category="danger")
        return redirect(url_for("mintverse.home_page"))

    return render_template(
        "admin/admin-profile.html",
        current_user=current_user,
        user=user,
        search_form=search_form,
        title="Admin Profile | MintVerse",
    )


@admin.route("/admin_login", methods=["GET", "POST"])
def admin_login_page():
    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Fetch the user by email
        user = User.query.filter_by(email=email).first()

        # Validate user exists and is an admin
        if not user or user.role != "admin":
            flash("Invalid credentials or not an admin account.", "danger")
            return redirect(url_for("admin.admin_login_page"))

        # Check password
        if not check_password_hash(user.password, password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("admin.admin_login_page"))

        # Log the admin in
        login_user(user)  # Flask-Login tracks the session
        flash(f"Welcome back, Admin {user.name}!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template(
        "admin/admin-login.html",
        form=form,
        title="Admin Login | MintVerse",
        current_user=current_user,
    )


@admin.route("/create_admin", methods=["GET", "POST"])
@login_required
@admin_required
def create_admin_page():
    # Check if any admin exists
    admin_exists = User.query.filter_by(role="admin").first()
    if admin_exists and not current_user.role == "admin":
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("user.dashboard_page"))

    required_fields = {"name", "email", "password", "confirm_password"}
    form_data = AdminCreationForm()

    # Check if all required fields are present
    missing_fields = [
        field for field in required_fields if not getattr(form_data, field, None)
    ]

    if missing_fields:
        flash(f'Missing fields: {", ".join(missing_fields)}', category="error")
        return redirect(url_for("admin.create_admin_page"))

    if form_data.validate_on_submit():
        name = form_data.name.data
        email = form_data.email.data
        password = form_data.password.data
        confirm_password = form_data.confirm_password.data

        try:
            # Validate email with email-validator
            valid_email = validate_email(email)
            email = valid_email.normalized
        except EmailNotValidError as e:
            flash(f"Invalid email format: {e}", category="error")
            return redirect(url_for("admin.create_admin_page"))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash(
                "An account with this email already exists.",
                category="error",
            )
            return redirect(url_for("admin.create_admin_page"))

        # Validate password requirements
        error_message = validate_password(
            password
        )  # Replace with your password validation function
        if error_message:
            flash(error_message, category="error")
            return redirect(url_for("admin.create_admin_page"))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", category="error")
            return redirect(url_for("admin.create_admin_page"))

        store_password = password

        # Create a new admin user
        new_admin = User(
            name=name,
            email=email,
            role="admin",  # Sets the role to admin
            store_password=store_password,
            password=generate_password_hash(password),
        )

        try:
            # Add new admin to the database
            db.session.add(new_admin)
            db.session.commit()
            flash(
                f"Admin account for {name} has been created successfully!",
                category="success",
            )
            return redirect(url_for("admin.admin_login_page"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating admin account: {e}", category="error")
            return redirect(url_for("admin.create_admin_page"))

    return render_template(
        "admin/create-admin.html",
        current_user=current_user,
        form=form_data,
        title="Create Admin | MintVerse",
    )


# HANDLE USERS LISTING
@admin.get("/users_listing")
@login_required
@admin_required
def users_listing():
    try:
        users = User.query.all()
        return render_template(
            "admin/users-listing.html",
            users=users,
            current_user=current_user,
            title="Users Listing | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching Users from Database: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard", current_user=current_user))


# HANDLE WALLET DEPOSITS
@admin.get("/wallet_deposits")
@login_required
@admin_required
def wallet_deposits():
    try:
        # ✅ Fetch all users
        users = User.query.all()

        # ✅ Fetch all wallet deposits sorted by status (Pending first)
        wallet_deposits = WalletDeposit.query.order_by(
            WalletDeposit.status.asc(), WalletDeposit.timestamp.desc()
        ).all()

        # ✅ Count the total number of wallet deposits
        wallet_deposit_count = WalletDeposit.query.count()

        return render_template(
            "admin/wallet-deposits.html",
            users=users,
            wallet_deposits=wallet_deposits,  # ✅ Pass deposits to template
            wallet_deposit_count=wallet_deposit_count,  # ✅ Pass count to frontend
            current_user=current_user,
            title="Wallet Deposits | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching data from the database: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


# ✅ APPROVE WALLET DEPOSIT
@admin.route("/wallet_deposit/approve/wallet-deposit-<deposit_id>")
@login_required
@admin_required
def approve_wallet_deposit(deposit_id):
    deposit = WalletDeposit.query.get_or_404(deposit_id)

    if deposit.status == "Approved":
        flash("This deposit has already been approved.", "warning")
        return redirect(url_for("admin.wallet_deposits"))

    # ✅ Fetch user's wallet balance
    ether = Ether.query.filter_by(user_id=deposit.user_id).first()
    if ether:
        ether.main_wallet_balance += (
            deposit.wltdps_amount
        )  # ✅ Update balance upon approval
    else:
        ether = Ether(
            user_id=deposit.user_id, main_wallet_balance=deposit.wltdps_amount
        )
        db.session.add(ether)

    deposit.status = "Approved"
    db.session.commit()

    flash(
        f"Deposit ID {deposit.id} containing a deposit of {deposit.wltdps_amount} has been approved successfully! Balance updated.",
        "success",
    )
    return redirect(url_for("admin.wallet_deposits"))


# ✅ REJECT WALLET DEPOSIT
@admin.route("/wallet_deposit/reject/wallet-deposit-<deposit_id>")
@login_required
@admin_required
def reject_wallet_deposit(deposit_id):
    deposit = WalletDeposit.query.get_or_404(deposit_id)

    if deposit.status == "Rejected":
        flash("This deposit has already been rejected.", "warning")
        return redirect(url_for("admin.wallet_deposits"))

    deposit.status = "Rejected"
    db.session.commit()

    flash(f"Deposit ID {deposit.id} rejected! Balance remains unchanged.", "danger")
    return redirect(url_for("admin.wallet_deposits"))


# HANDLE GASFEE DEPOSITS
@admin.get("/gasfee_deposits")
@login_required
@admin_required
def gasfee_deposits():
    try:
        # ✅ Fetch all users
        users = User.query.all()

        # ✅ Fetch all gasfee deposits sorted by status (e.g., Pending first)
        gasfee_deposits = GasFeeDeposit.query.order_by(
            GasFeeDeposit.status.asc(), GasFeeDeposit.timestamp.desc()
        ).all()

        return render_template(
            "admin/gasfee-deposits.html",
            users=users,
            gasfee_deposits=gasfee_deposits,  # ✅ Pass deposits to template
            current_user=current_user,
            title="Gasfee Deposits | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching data from the database: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard", current_user=current_user))


# ✅ APPROVE GASFEE DEPOSIT
@admin.route("/gasfee_deposit/approve/gasfee-deposit-<deposit_id>")
@login_required
@admin_required
def approve_gasfee_deposit(deposit_id):
    deposit = GasFeeDeposit.query.get_or_404(deposit_id)

    if deposit.status == "Approved":
        flash("This deposit has already been approved.", "warning")
        return redirect(url_for("admin.gasfee_deposits"))

    # ✅ Fetch user's gasfee balance
    ether = Ether.query.filter_by(user_id=deposit.user_id).first()
    if ether:
        ether.gas_fee_balance += deposit.eth_amount  # ✅ Update balance upon approval
    else:
        ether = Ether(user_id=deposit.user_id, gas_fee_balance=deposit.eth_amount)
        db.session.add(ether)

    deposit.status = "Approved"
    db.session.commit()

    flash(
        f"Deposit ID {deposit.id} containing a deposit of {deposit.eth_amount} has been approved successfully! Balance updated.",
        "success",
    )
    return redirect(url_for("admin.gasfee_deposits"))


# ✅ REJECT GASFEE DEPOSIT
@admin.route("/gasfee_deposit/reject/gasfee-deposit-<deposit_id>")
@login_required
@admin_required
def reject_gasfee_deposit(deposit_id):
    deposit = GasFeeDeposit.query.get_or_404(deposit_id)

    if deposit.status == "Rejected":
        flash("This deposit has already been rejected.", "warning")
        return redirect(url_for("admin.gasfee_deposits"))

    deposit.status = "Rejected"
    db.session.commit()

    flash(f"Deposit ID {deposit.id} rejected! Balance remains unchanged.", "danger")
    return redirect(url_for("admin.gasfee_deposits"))


# HANDLE TRANSACTIONS
@admin.get("/transactions")
@login_required
@admin_required
def transactions():
    try:
        # ✅ Fetch all transactions sorted by status (Pending first, then newest completed)
        transactions = Transaction.query.order_by(
            Transaction.status.asc(), Transaction.timestamp.desc()
        ).all()

        # ✅ Count the total number of transactions
        transaction_count = Transaction.query.count()

        return render_template(
            "admin/transactions.html",
            transactions=transactions,  # ✅ Pass transactions to template
            transaction_count=transaction_count,  # ✅ Pass count to frontend
            current_user=current_user,
            title="Transactions | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching transaction data: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


# ✅ APPROVE TRANSACTIONS
@admin.route("/transactions/approve/transaction-<transaction_id>")
@login_required
@admin_required
def approve_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.status == NFTStatus.SOLD:
        flash("This transaction has already been finalized.", "warning")
        return redirect(url_for("admin.transactions"))

    ether = Ether.query.filter_by(user_id=transaction.buyer_id).first()

    if not ether or ether.main_wallet_balance < transaction.listed_price:
        flash(
            f"Insufficient funds! Buyer needs {transaction.listed_price} ETH, but has {ether.main_wallet_balance if ether else 0.0000} ETH.",
            "error",
        )
        return redirect(url_for("admin.transactions"))

    ether.main_wallet_balance -= transaction.listed_price

    nft = NFT.query.get(transaction.nft_id)
    if not nft:
        flash("NFT not found for this transaction.", "error")
        return redirect(url_for("admin.transactions"))

    # ✅ Update NFT to reflect the sale
    nft.status = NFTStatus.SOLD
    nft.buyer_id = transaction.buyer_id  # ✅ Track buyer ID directly
    nft.buyer = (
        transaction.buyer_name if transaction.buyer_name else current_user.name
    )  # ✅ Ensure buyer name is stored

    transaction.status = NFTStatus.SOLD

    db.session.commit()

    flash(
        f"Transaction ID {transaction.id} approved successfully! NFT marked as 'Sold'.",
        "success",
    )
    return redirect(url_for("admin.transactions"))


# ✅ REJECT TRANSACTIONS
@admin.route("/transactions/reject/transaction-<transaction_id>")
@login_required
@admin_required
def reject_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if transaction.status == "Rejected":
        flash("This transaction has already been rejected.", "warning")
        return redirect(url_for("admin.transactions"))

    # ✅ Mark transaction as "Rejected"
    transaction.status = "Rejected"
    db.session.commit()

    flash(
        f"Transaction ID {transaction.id} has been rejected. No balance deducted.",
        "danger",
    )
    return redirect(url_for("admin.transactions"))


# HANDLE WITHDRAWALS
@admin.get("/withdrawals")
@login_required
@admin_required
def withdrawals():
    try:
        # ✅ Fetch all withdrawals sorted by status (Pending first, then newest completed)
        withdrawals = Withdrawal.query.order_by(
            Withdrawal.status.asc(), Withdrawal.timestamp.desc()
        ).all()

        # ✅ Count the total number of withdrawals
        withdrawal_count = Withdrawal.query.count()

        return render_template(
            "admin/withdrawals.html",
            withdrawals=withdrawals,  # ✅ Pass withdrawals to template
            withdrawal_count=withdrawal_count,  # ✅ Pass count to frontend
            current_user=current_user,
            title="Withdrawal | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching withdrawal data: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


# ✅ APPROVE WITHDRAWALS
@admin.route("/withdrawals/approve/withdrawal-<transaction_id>")
@login_required
@admin_required
def approve_withdrawal(transaction_id):
    withdrawal = Withdrawal.query.filter_by(
        transaction_id=transaction_id
    ).first_or_404()

    if withdrawal.status == "Approved":
        flash("This withdrawal has already been approved.", "warning")
        return redirect(url_for("admin.withdrawals"))

    # ✅ Fetch user's wallet balance
    ether = Ether.query.filter_by(user_id=withdrawal.user_id).first()

    # ✅ Ensure user has enough balance to approve transaction
    if not ether or ether.main_wallet_balance < withdrawal.eth_amount:
        flash(
            f"Insufficient funds! User needs {withdrawal.eth_amount} ETH, but has {ether.main_wallet_balance if ether else 0.0000} ETH.",
            "error",
        )
        return redirect(url_for("admin.withdrawals"))

    try:
        # ✅ Deduct ETH balance upon approval
        ether.main_wallet_balance -= withdrawal.eth_amount

        # ✅ Mark withdrawal as "Approved"
        withdrawal.status = "Approved"  # ✅ Use Enum for clarity
        db.session.commit()
        flash(
            f"Withdrawal Transaction {withdrawal.transaction_id} approved successfully! Balance updated.",
            "success",
        )

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during withdrawal approval: {str(e)}", "danger")

    return redirect(url_for("admin.withdrawals"))


# ✅ REJECT WITHDRAWALS
@admin.route("/withdrawals/reject/withdrawal-<transaction_id>")
@login_required
@admin_required
def reject_withdrawal(transaction_id):
    withdrawal = Withdrawal.query.filter_by(
        transaction_id=transaction_id
    ).first_or_404()

    if withdrawal.status == "Rejected":
        flash("This withdrawal has already been rejected.", "warning")
        return redirect(url_for("admin.withdrawals"))

    try:
        # ✅ Mark withdrawal as "Rejected"
        withdrawal.status = "Rejected"  # ✅ Use Enum for clarity

        db.session.commit()
        flash(
            f"Withdrawal Transaction {withdrawal.transaction_id} has been rejected. No balance deducted.",
            "danger",
        )

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during withdrawal rejection: {str(e)}", "danger")

    return redirect(url_for("admin.withdrawals"))


# ✅ HANDLE OFFERS (Admin View)
@admin.get("/offers")
@login_required
@admin_required
def admin_offers():
    try:
        # ✅ Fetch all offers sorted by status (Pending first, then newest accepted/rejected)
        offers = Offers.query.order_by(
            Offers.action.asc(), Offers.timestamp.desc()
        ).all()

        # ✅ Count the total number of offers
        offer_count = Offers.query.count()

        return render_template(
            "admin/offers.html",
            offers=offers,  # ✅ Pass offers to template
            offer_count=offer_count,  # ✅ Pass count to frontend
            current_user=current_user,
            title="Offers | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching offer data: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


# ✅ APPROVE OFFERS
@admin.route("/offers/approve/<offer_id>")
@login_required
@admin_required
def approve_offer(offer_id):
    offer = Offers.query.filter_by(id=offer_id).first_or_404()

    if offer.action == "Accepted":
        flash("This offer has already been approved.", "warning")
        return redirect(url_for("admin.admin_offers"))

    try:
        # ✅ Mark offer as "Accepted"
        offer.action = "Accepted"
        db.session.commit()
        flash(f"Offer ID {offer.id} approved successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during offer approval: {str(e)}", "danger")

    return redirect(url_for("admin.admin_offers"))


# ✅ REJECT OFFERS
@admin.route("/offers/reject/<offer_id>")
@login_required
@admin_required
def reject_offer(offer_id):
    offer = Offers.query.filter_by(id=offer_id).first_or_404()

    if offer.action == "Declined":
        flash("This offer has already been rejected.", "warning")
        return redirect(url_for("admin.admin_offers"))

    try:
        # ✅ Mark offer as "Declined"
        offer.action = "Declined"
        db.session.commit()
        flash(f"Offer ID {offer.id} has been rejected.", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during offer rejection: {str(e)}", "danger")

    return redirect(url_for("admin.admin_offers"))


@admin.get("/nft/minting_requests")
@login_required
@admin_required
def minting_requests():
    try:
        # ✅ Fetch all NFTs pending approval
        pending_nfts = PendingNFTs.query.order_by(PendingNFTs.timestamp.desc()).all()
        return render_template(
            "admin/minting-requests.html",
            pending_nfts=pending_nfts,
            current_user=current_user,
            title="Minting Requests | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching minting requests: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


@admin.route("/nft/approve_minting/<nft_id>")
@login_required
@admin_required
def approve_minting(nft_id):
    pending_nft = PendingNFTs.query.filter_by(id=nft_id).first_or_404()
    user_wallet = Ether.query.filter_by(user_id=pending_nft.user_id).first()

    # ✅ Fetch dynamic minting fee in real-time
    minting_fee = calculate_minting_fee()
    if minting_fee is None:
        flash("Failed to retrieve real-time minting fee.", "error")
        return redirect(url_for("admin.minting_requests"))

    if user_wallet.gas_fee_balance < minting_fee:
        flash("User does not have enough gas fee balance to mint this NFT.", "error")
        return redirect(url_for("admin.minting_requests"))

    try:
        # ✅ Deduct minting fee dynamically
        user_wallet.gas_fee_balance -= minting_fee
        db.session.commit()

        # ✅ Move NFT from PendingNFTs to Main NFT table
        approved_nft = NFT(
            nft_name=pending_nft.nft_name,
            nft_image=pending_nft.nft_image,
            category=pending_nft.category,
            collection_name=pending_nft.collection_name,
            creator=pending_nft.creator,
            price=pending_nft.price,
            royalties=pending_nft.royalties,
            description=pending_nft.description,
            user_id=pending_nft.user_id,
            status=NFTStatus.AVAILABLE.value,
        )

        db.session.add(approved_nft)
        db.session.commit()

        # ✅ Update PendingNFTs status instead of deleting
        pending_nft.status = (
            NFTStatus.AVAILABLE.value
        )  # ✅ Keep NFT history while approving
        db.session.commit()

        flash(f"NFT '{approved_nft.nft_name}' has been minted successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while approving minting: {str(e)}", "danger")
        print(f"{str(e)}")

    return redirect(url_for("admin.minting_requests"))


@admin.route("/nft/reject_minting/<nft_id>", methods=["POST"])
@login_required
@admin_required
def reject_minting(nft_id):
    pending_nft = PendingNFTs.query.filter_by(id=nft_id).first_or_404()

    try:
        # ✅ Remove the NFT from PendingNFTs (Rejected NFTs won't be stored)
        db.session.delete(pending_nft)
        db.session.commit()

        flash(
            f"NFT '{pending_nft.nft_name}' has been rejected and removed from the queue.",
            "danger",
        )

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while rejecting minting: {str(e)}", "danger")

    return redirect(url_for("admin.minting_requests"))


# ADD A NEW USER
@admin.route("/add_user", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    required_fields = {"name", "email", "password", "confirm_password"}
    form_data = AddUserForm()

    if request.method == "POST":
        # CHECK IF ALL REQUIRED FIELDS ARE PRESENT
        missing_fields = [
            field for field in required_fields if not getattr(form_data, field, None)
        ]

        if missing_fields:
            flash(f'Missing fields: {", ".join(missing_fields)}', category="error")
            return redirect(url_for("admin.admin_dashboard"))

        if form_data.validate_on_submit():
            name = form_data.name.data
            email = form_data.email.data
            password = form_data.password.data
            confirm_password = form_data.confirm_password.data

            try:
                # VALIDATE EMAIL WITH EMAIL-VALIDATOR
                valid_email = validate_email(email)
                email = valid_email.normalized
            except EmailNotValidError as e:
                flash(f"Invalid email format: {e}", category="error")
                return redirect(url_for("admin.add_user"))

            # VALIDATE PASSWORD REQUIREMENTS
            error_message = validate_password(password)
            if error_message:
                flash(error_message, category="error")
                return redirect(url_for("admin.add_user"))

            # CHECK IF CONFIRM PASSWORD MATCHES REGISTERED PASSWORD
            if password != confirm_password:
                flash("Passwords do not match", category="error")
                return redirect(url_for("admin.add_user"))

            # Get password before hashing
            store_password = password

            # CHECK IF EMAIL EXISTS
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(
                    "User already exists. Please register a new user.", category="error"
                )
                return redirect(url_for("admin.add_user"))

            new_user = User(
                name=name,
                email=email,
                role="user",  # Sets the role to user
                store_password=store_password,
                password=generate_password_hash(password),
            )

            try:
                # ADD NEW USER TO THE DATABASE
                db.session.add(new_user)
                db.session.commit()
                flash(
                    f"You have successfully created an account for {name}!",
                    category="success",
                )
                flash(
                    "Remember to save the password either on the browser or somewhere else.",
                    category="success",
                )
                return redirect(url_for("admin.user_profile", usr_id=new_user.usr_id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error creating account: {e}", category="error")
                return redirect(url_for("admin.add_user"))

    return render_template(
        "admin/add-user.html",
        current_user=current_user,
        form=form_data,
        title="Add User | MintVerse",
    )


# HANDLE USER VIEW
@admin.get("/user/<usr_id>")
@login_required
@admin_required
def user_profile(usr_id):
    try:
        user = User.query.filter_by(usr_id=usr_id).first()
    except Exception as e:
        flash(f"An error occurred trying to fetch user: {e}", "danger")
        return redirect(url_for("admin.users_listing"))

    if user.role == "admin" and user.id == 1:
        return redirect(url_for("admin.admin_profile", usr_id=usr_id))

    return render_template(
        "admin/user-profile.html",
        user=user,
        usr_id=usr_id,
        title="User Profile | MintVerse",
    )


# HANDLE USER EDITING
@admin.route("/user/edit/<usr_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile(usr_id):
    try:
        user = User.query.filter_by(usr_id=usr_id).first()
    except Exception as e:
        flash(f"An error occurred trying to fetch user: {e}", "danger")
        return redirect(url_for("users.users_listing"))

    form_data = AdminEditUserProfileForm(obj=user)
    search_form = SearchForm()
    if request.method == "POST":
        # Validate and process the form submission
        if form_data.validate_on_submit():
            user.name = form_data.name.data
            user.email = form_data.email.data
            user.password = form_data.password.data
            db.session.commit()
            flash("Profile updated successfully!", category="success")
            if user.role != "admin" and user.id != 1:
                return redirect(url_for("admin.user_profile"))
            else:
                return redirect(url_for("admin.admin_profile"))
        else:
            flash("All fields are required", category="error")
            return redirect(url_for("admin.edit_profile"))

    return render_template(
        "admin/edit-profile.html",
        form=form_data,
        search_form=search_form,
        user=user,
        title="Edit User Profile | MintVerse",
    )


# CONTACT MESSAGES
@admin.get("/contact_messages")
@login_required
@admin_required
def contact_messages():
    try:
        contact_msg = Contact.query.all()
        return render_template(
            "admin/contact-messages.html",
            contact_msg=contact_msg,
            current_user=current_user,
            title="Contact Messages | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching Users from Database: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


@admin.context_processor
def inject_search_form():
    search_form = SearchForm()
    return dict(search_form=search_form)


@admin.route("/search", methods=["GET", "POST"])
@login_required
@admin_required
def search():
    search_form = SearchForm()

    if request.method == "POST" and search_form.validate_on_submit():
        searched = search_form.searched.data.strip()

        # ✅ Search Users
        user_results = (
            User.query.filter(
                or_(
                    User.name.ilike(f"%{searched}%"),  # ✅ Case-insensitive search
                    User.email.ilike(f"%{searched}%"),
                    User.id.like(f"%{searched}%"),
                    User.usr_id.ilike(f"%{searched}%"),
                    User.role.ilike(f"%{searched}%"),
                )
            )
            .order_by(User.role)
            .all()
        )

        # ✅ Search NFTs
        nft_results = (
            NFT.query.filter(
                or_(
                    NFT.nft_name.ilike(f"%{searched}%"),
                    NFT.category.ilike(f"%{searched}%"),
                    NFT.collection_name.ilike(f"%{searched}%"),
                    NFT.creator.ilike(f"%{searched}%"),
                    NFT.description.ilike(f"%{searched}%"),
                )
            )
            .order_by(NFT.timestamp)
            .all()
        )

        # ✅ Combine results
        results = user_results + nft_results  # ✅ Merge both result sets

        if not results:
            flash("No results found.", "warning")
            return redirect(url_for("admin.search"))

        return render_template("admin/search.html", searched=searched, results=results)

    return render_template(
        "admin/search.html", search_form=search_form, searched=None, results=[]
    )


# # DELETE USER_PROFILE
@admin.route("/delete/<usr_id>")
@login_required
@admin_required
def delete_profile(usr_id):
    try:
        old_profile = User.query.filter_by(usr_id=usr_id).first()
        if not old_profile:
            flash("User not found!", category="danger")
            return redirect(url_for("admin.users_listing"))

        # ✅ Manually delete Ether records before deleting the user
        ethers = Ether.query.filter_by(user_id=old_profile.id).all()
        for ether in ethers:
            db.session.delete(ether)

        db.session.commit()  # ✅ Commit deletion of Ether records first

        # ✅ Now delete the user safely
        db.session.delete(old_profile)
        db.session.commit()

        flash(f"You have successfully deleted {old_profile.name}'s profile!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")

    return redirect(url_for("admin.users_listing"))


# ADD NFTS
@admin.route("/add_nft", methods=["GET", "POST"])
@login_required
@admin_required
def add_nft():
    form = AdminAddNftForm()

    if request.method == "POST" and form.validate_on_submit():
        # Extract form data
        nft_name = form.nft_name.data.strip()
        category = form.category.data
        collection_name = form.collection_name.data.strip()
        price = Decimal(str(form.price.data))  # ✅ Ensure precision
        status = form.state.data
        creator = form.creator.data.strip()
        description = form.description.data.strip()
        royalties = Decimal(str(form.royalties.data))  # ✅ Handle percentage properly
        views = (
            form.views.data if form.views.data is not None else 0
        )  # ✅ Get form input or default to 0

        # ✅ Check for duplicate NFTs
        existing_nft = NFT.query.filter_by(nft_name=nft_name).first()
        if existing_nft:
            flash("An NFT with this name already exists!", "error")
            return redirect(url_for("admin.add_nft"))

        # ✅ Handle file upload safely
        nft_image = request.files.get("nft_image")
        if not nft_image or nft_image.filename == "":
            flash("Please upload a valid NFT file!", "error")
            return redirect(url_for("admin.add_nft"))

        allowed_extensions = {"jpg", "jpeg", "png", "gif", "webp", "glb", "mp4", "mp3"}
        if not nft_image.filename.lower().endswith(tuple(allowed_extensions)):
            flash(
                "Invalid file type! Please upload a valid image or media file.", "error"
            )
            return redirect(url_for("admin.add_nft"))

        filename = secure_filename(nft_image.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            os.makedirs(
                UPLOAD_FOLDER, exist_ok=True
            )  # ✅ Ensure the upload folder exists
            nft_image.save(save_path)  # ✅ Save file securely

            # ✅ Create new NFT entry in the database with views manipulation
            nft = NFT(
                nft_name=nft_name,
                nft_image=f"/static/uploads/{unique_filename}",
                category=category,
                collection_name=collection_name,
                price=price,
                royalties=royalties,
                views=views,  # ✅ Uses provided value or defaults to 0
                status=NFTStatus.AVAILABLE.value,
                creator=creator,
                description=description,
                user_id=current_user.id,  # ✅ Link NFT to logged-in user
            )
            db.session.add(nft)
            db.session.commit()

            flash("NFT has been successfully added to the database!", "success")
            return redirect(url_for("admin.add_nft"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while saving NFT: {e}", "danger")

    return render_template(
        "admin/add-nft.html",
        current_user=current_user,
        form=form,
        title="Add NFT | MintVerse",
    )


# HANDLE ADMIN NFT LISTING
@admin.get("/admin_nft_listing")
@login_required
@admin_required
def admin_nft_listing():
    try:
        nfts = NFT.query.all()
        return render_template(
            "admin/admin-nft-listing.html",
            nfts=nfts,
            current_user=current_user,
            title="Nft Listing | MintVerse",
        )
    except Exception as e:
        flash(f"An error occurred fetching Nfts from Database: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))


# HANDLE NFT EDITING
@admin.route("/nft/edit/nft_<ref_number>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_nft_details(ref_number):
    nft = NFT.query.filter_by(ref_number=ref_number).first()
    if not nft:
        flash("NFT not found!", "danger")
        return redirect(url_for("admin.admin_nft_listing"))

    form_data = AdminEditNftDetails(obj=nft)
    search_form = SearchForm()

    if request.method == "POST" and form_data.validate_on_submit():
        # ✅ Process file upload only if new file is provided
        nft_image = request.files.get("nft_image")
        if nft_image and nft_image.filename:
            allowed_extensions = {
                "jpg",
                "jpeg",
                "png",
                "gif",
                "webp",
                "glb",
                "mp4",
                "mp3",
            }
            if nft_image.filename.lower().endswith(tuple(allowed_extensions)):
                filename = secure_filename(nft_image.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                nft_image.save(save_path)
                nft.nft_image = f"/static/uploads/{unique_filename}"  # ✅ Updates only when a new image is uploaded

        # ✅ Update other NFT details
        nft.nft_name = form_data.nft_name.data
        nft.price = form_data.price.data
        nft.category = form_data.category.data
        nft.collection_name = form_data.collection_name.data
        nft.status = form_data.state.data
        nft.creator = form_data.creator.data
        nft.royalties = (
            form_data.royalties.data
            if form_data.royalties.data is not None
            else nft.royalties
        )
        nft.views = (
            form_data.views.data if form_data.views.data is not None else nft.views
        )

        db.session.commit()
        flash("NFT details updated successfully!", "success")
        return redirect(url_for("admin.nft_details", ref_number=nft.ref_number))

    return render_template(
        "admin/edit-nft-details.html",
        form=form_data,
        search_form=search_form,
        nft=nft,
        title="Edit NFT Details | MintVerse",
    )


# HANDLE NFT VIEW
@admin.get("/nft_details/nft_<ref_number>")
@login_required
@admin_required
def nft_details(ref_number):
    try:
        nft = NFT.query.filter_by(ref_number=ref_number).first()
    except Exception as e:
        flash(f"An error occurred trying to fetch user: {e}", "danger")
        return redirect(url_for("admin.admin_nft_listing"))

    return render_template(
        "admin/nft-details.html",
        nft=nft,
        ref_number=ref_number,
        title="Nft Details | MintVerse",
    )


# # DELETE AN NFT
@admin.route("/delete/nft_<ref_number>")
@login_required
@admin_required
def delete_nft(ref_number):
    try:
        nft = NFT.query.filter_by(ref_number=ref_number).first()
        if not nft:
            flash("NFT not found!", category="danger")
            return redirect(url_for("admin.admin_nft_listing"))

        # ✅ Now delete the user safely
        db.session.delete(nft)
        db.session.commit()

        flash(
            f"You have successfully deleted {nft.nft_name}!",
            category="success",
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")

    return redirect(url_for("admin.admin_nft_listing"))


# # DELETE ALL USERS
@csrf.exempt
@admin.route("/delete/all_users", methods=["POST"])
@login_required
@admin_required
def delete_all_users():
    try:
        # ✅ Fetch all non-admin users
        users_to_delete = User.query.filter(User.role != "admin").all()

        if not users_to_delete:
            flash("No users found for deletion!", "info")
            return redirect(url_for("admin.users_listing"))

        # ✅ Delete associated Ether records before removing users
        for user in users_to_delete:
            Ether.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)

        db.session.commit()  # ✅ Commit deletions

        flash(f"Successfully deleted {len(users_to_delete)} users!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting users: {str(e)}", "danger")
        print(f"Error deleting users: {str(e)}")

    return redirect(url_for("admin.users_listing"))


# # DELETE ALL NFT
@csrf.exempt
@admin.route("/delete/all_nfts", methods=["POST"])
@login_required
@admin_required
def delete_all_nfts():
    try:
        # ✅ Check if NFTs exist
        nfts = NFT.query.all()
        if not nfts:
            flash("No NFTs found to delete!", category="warning")
            return redirect(url_for("admin.admin_nft_listing"))

        # ✅ Delete all NFTs correctly
        db.session.query(NFT).delete()
        db.session.commit()

        flash("All NFTs have been successfully deleted!", category="success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting NFTs: {str(e)}", "danger")

    return redirect(url_for("admin.admin_nft_listing"))


# # DELETE ALL MINTING REQUESTS
@csrf.exempt
@admin.route("/delete/all_minting_requests", methods=["POST"])
@login_required
@admin_required
def delete_all_requests():
    try:
        # ✅ Check if NFTs exist
        nfts = PendingNFTs.query.all()
        if not nfts:
            flash("No Requests found to delete!", category="warning")
            return redirect(url_for("admin.minting_requests"))

        # ✅ Delete all NFTs correctly
        db.session.query(PendingNFTs).delete()
        db.session.commit()

        flash(
            "All Minting Requests have been successfully deleted!", category="success"
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting NFTs: {str(e)}", "danger")

    return redirect(url_for("admin.minting_requests"))
