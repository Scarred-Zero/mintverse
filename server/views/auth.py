from datetime import datetime
from flask import Blueprint, request, render_template, redirect, flash, url_for, current_app
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# ✅ Database & Models
from ..config.database import db
from ..models.User import User
from ..models.Ether import Ether

# ✅ Utilities & Helpers
from ..utils.mail_handler import generate_verification_token, send_verification_email, verify_token
from ..utils.helpers import validate_password
from email_validator import validate_email, EmailNotValidError

# ✅ Forms
from .forms import LoginForm, PasswordResetForm, PasswordResetRequestForm, RegistrationForm, SearchForm  # ChangePasswordForm

from flask_mail import Message
from server import mail

# ✅ Create Authentication Blueprint
auth = Blueprint("auth", __name__)


@auth.context_processor
def inject_search_form():
    return dict(form=SearchForm())


# ✅ Handle User Login
@auth.route("/login", methods=["GET", "POST"])
def login_page():
    form_data = LoginForm()

    if form_data.validate_on_submit():
        email = form_data.email.data
        password = form_data.password.data

        # ✅ Validate Email & Password
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "warning")
            return redirect(url_for("auth.login_page"))

        # ✅ Exclude admins from email verification check
        if not user.is_email_verified and user.role != "admin":
            flash(
                "You must verify your email before logging in. Check your inbox for a verification link.",
                "warning",
            )
            send_verification_email(user)
            return redirect(url_for("auth.login_page"))

        # ✅ Login User (Admins bypass verification)
        login_user(user, remember=True)
        flash(f"Welcome to MintVerse, {user.name}!", "success")

        return redirect(
            url_for(
                (
                    "admin.admin_dashboard"
                    if user.role == "admin"
                    else "user.dashboard_page"
                ),
            )
        )

    return render_template(
        "auth/pages/login.html",
        current_user=current_user,
        form=form_data,
        title="Log In | MintVerse",
    )


# ✅ Handle User Registration
@auth.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegistrationForm()

    if request.method == "POST" and form.validate_on_submit():
        name, email, password, confirm_password = (
            form.name.data.strip(),
            form.email.data,
            form.password.data,
            form.confirm_password.data,
        )
        try:
            name_parts = name.strip().split()

            if len(name_parts) == 1:
                name = name_parts[0]  # ✅ Single word, strip all extra spaces
            elif len(name_parts) == 2:
                name = " ".join(name_parts)  # ✅ Two words, ensure only one space
            elif len(name_parts) > 2:
                flash("Please enter a valid name (either first name or first & last name only).", "warning")
                return redirect(url_for("auth.register_page"))

            # ✅ Ensure name contains only alphabetic characters
            if not all(part.isalpha() for part in name_parts):
                flash("Names can only contain letters. No numbers or symbols allowed.", "warning")
                return redirect(url_for("auth.register_page"))

        except Exception as e:
            flash(f"An error occurred while processing the name: {str(e)}", "warning")
            return redirect(url_for("auth.register_page"))

        # ✅ Validate Email Format
        try:
            email = validate_email(email).normalized
        except EmailNotValidError as e:
            flash(f"Invalid email format: {e}", "warning")
            return redirect(url_for("auth.register_page"))

        # ✅ Check if Email Already Registered
        if User.query.filter_by(email=email).first():
            flash("User already exists. Please login instead.", "warning")
            return redirect(url_for("auth.register_page"))

        # ✅ Validate Password Requirements
        if (error_msg := validate_password(password)) or password != confirm_password:
            flash(error_msg or "Passwords do not match", "warning")
            return redirect(url_for("auth.register_page"))

        # Get password before hashing
        store_password = password

        try:
            # ✅ Create New User
            new_user = User(
                name=name,
                email=email,
                role="user",
                store_password=store_password,
                password=generate_password_hash(password),
            )
            db.session.add(new_user)
            db.session.flush()

            # ✅ Initialize Ether Balance
            db.session.add(Ether(user_id=new_user.id, main_wallet_balance=0.0000))
            db.session.commit()

            flash(f"Hey {name}, your account was created successfully!", "success")

            # ✅ Send Email Verification
            flash("Check the 'Spam folder' or 'Inbox' in your email for a verification link.", "warning")
            send_verification_email(new_user)
            return redirect(url_for("auth.login_page"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {e}", "warning")
            return redirect(url_for("auth.register_page"))

    return render_template(
        "auth/pages/register.html",
        current_user=current_user,
        form=form,
        title="Register | MintVerse",
    )


# ✅ Email Verification Route
@auth.route("/verify_email/<token>")
def verify_email(token):
    email = verify_token(token)
    if not email or not (user := User.query.filter_by(email=email).first()):
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.login_page"))

    user.is_email_verified = True
    db.session.commit()
    flash("Your email has been verified!", "success")
    return redirect(url_for("auth.login_page"))


# ✅ Handle User Logout
@auth.get("/logout")
@login_required
def logout():
    flash(f"{current_user.name}, you've been logged out!", "success")
    logout_user()
    return redirect(url_for("auth.login_page"))


@auth.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        email = form.email.data

        try:
            email = validate_email(email).normalized
        except EmailNotValidError as e:
            flash(f"Invalid email format: {e}", "warning")
            return redirect(url_for("auth.request_password_reset"))

        try:
            user = User.query.filter_by(email=email).first()

            if user:
                token = generate_verification_token(user.email)
                verify_url = url_for("auth.reset_password", token=token, _external=True)


                msg = Message(
                    "Password Reset Request",
                    sender=current_app.config["MAIL_USERNAME"],
                    recipients=[user.email],
                )
                msg.body = f"Click the link to reset your password: {verify_url}"

                try:
                    mail.send(msg)
                    flash("Password reset email sent! Check your inbox.", "success")
                except Exception as mail_error:
                    flash(f"Error sending email: {mail_error}", "warning")

            else:
                flash("No account found with that email.", "danger")

        except Exception as db_error:
            flash(f"Database error: {db_error}", "warning")

    return render_template("auth/pages/request-password-reset.html", form=form)


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:
        email = verify_token(token)
        if not email or not (user := User.query.filter_by(email=email).first()):
            flash("Invalid or expired token.", "danger")
            return redirect(url_for("auth.request_password_reset"))

        form = PasswordResetForm()

        if form.validate_on_submit():
            password = form.password.data
            confirm_password = form.confirm_password.data

            try:
                # ✅ Validate Password Requirements
                if (
                    error_msg := validate_password(password)
                ) or password != confirm_password:
                    flash(error_msg or "Passwords do not match", "warning")
                    return redirect(url_for("auth.reset_password", token=token))

                user.reset_password(password)
                flash("Password reset successful! You can now log in.", "success")
                return redirect(url_for("auth.login_page"))

            except Exception as password_error:
                flash(f"Error updating password: {password_error}", "warning")

    except Exception as db_error:
        flash(f"Database error: {db_error}", "warning")

    return render_template("auth/pages/reset-password.html", form=form)
