from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from server import mail


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )  # ✅ Use current_app instead of creating a new instance
    return serializer.dumps(email, salt="email-confirmation-salt")


def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(
            token, salt="email-confirmation-salt", max_age=expiration
        )
    except:
        return None


def send_verification_email(user):
    token = generate_verification_token(user.email)
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    msg = Message(
        "Verify Your Email - MintVerse",
        sender=current_app.config[
            "MAIL_USERNAME"
        ],  # ✅ Use current_app instead of direct Flask app
        recipients=[user.email],
    )
    msg.body = f"Hello {user.name},\n\nClick the link below to verify your email:\n{verify_url}\n\nIf you didn't request this, ignore this message."

    mail.send(msg)
