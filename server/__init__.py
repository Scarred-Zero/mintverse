import os
import traceback
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager
from flask_mail import Mail
from web3 import Web3
from .utils.creating_admin import create_admin_on_startup
from .config.database import db
from flask_migrate import Migrate
from .models.User import User
from .config.variables import (
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    MAIL_PASSWORD,
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
)
from flask_wtf.csrf import CSRFProtect


UPLOAD_FOLDER = os.path.join("server/static/uploads")

# ✅ Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Initialize Flask-Mail globally
mail = Mail()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    csrf.init_app(app)
    w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))

    # ✅ CONFIGURATIONS
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_TYPE"] = "filesystem"  # Store session data persistently

    # DATABASE CONFIGS
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
    app.config["SQLALCHEMY_POOL_PRE_PING"] = True

    # MAIL CONFIGS
    app.config["MAIL_SERVER"] = MAIL_SERVER
    app.config["MAIL_PORT"] = MAIL_PORT
    app.config["MAIL_USERNAME"] = MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_TIMEOUT"] = 60

    # ✅ Initialize Flask-Mail and Database
    mail.init_app(app)
    db.init_app(app)

    # ✅ Register Blueprints
    from .views.auth import auth
    from .views.routes import mintverse
    from .views.admin import admin
    from .views.user import user
    from .views.category import category

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(mintverse)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(category, url_prefix="/category")

    # Models
    from . import models

    create_database(app)
    migrate = Migrate(app, db)

    # Create Admin
    with app.app_context():
        create_admin_on_startup()

    # ✅ Setup Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login_page"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(usr_id):
        return User.query.get(usr_id)

    @login_manager.unauthorized_handler
    def handle_needs_login():
        flash("You have to be logged in to access this page.")
        return redirect(url_for("auth.login_page"))

    # ✅ Error Handling
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/error-404.html", title="404 ERROR | MintVerse")

    @app.errorhandler(Exception)
    def server_error(error):
        traceback.print_exc()
        db.session.rollback()
        return render_template(
            "errors/server-error.html", title="SERVER ERROR | MintVerse"
        )

    @app.route("/verify_wallet", methods=["POST"])
    def verify_wallet():
        wallet_address = request.json.get("address")

        if not wallet_address:
            return (
                jsonify({"status": "error", "message": "Wallet address missing!"}),
                400,
            )

        if w3.is_address(wallet_address):
            return jsonify({"status": "success", "message": "Wallet verified!"})
        else:
            return (
                jsonify({"status": "error", "message": "Invalid wallet address!"}),
                400,
            )

    # Route for updating the wallet in backend storage
    @app.route("/update_wallet", methods=["POST"])
    def update_wallet():
        wallet_address = request.json.get("wallet_address")

        if not wallet_address:
            return (
                jsonify({"status": "error", "message": "Wallet address missing!"}),
                400,
            )

        if not w3.is_address(wallet_address):
            return (
                jsonify({"status": "error", "message": "Invalid wallet address!"}),
                400,
            )

        # Mock storage (replace with actual database save logic)
        # Example: Save to database or session
        wallet_data = {"wallet_address": wallet_address}

        return jsonify(
            {"status": "success", "message": "Wallet stored!", "data": wallet_data}
        )

    return app


def create_database(app):
    with app.app_context():
        db.create_all()
        print(" * Database tables initialized (if not already present)!")
