from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer
from ..config.variables import (
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_SERVER,
    MAIL_DEFAULT_FROM,
)
from email.message import EmailMessage
import smtplib


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

    subject = "Verify Your Email - MintVerse"
    recipient = user.email
    plain_text = f"Hello {user.name},\n\nClick the link below to verify your email:\n{verify_url}\n\nIf you didn't request this, ignore this message."
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Verify Your Email Address</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f4f4;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.05);">
                        <tr>
                            <td align="center" style="padding: 30px; background-color: #007bff;">
                                <h1 style="font-family: sans-serif; color: #ffffff; margin: 0;">MintVerse</h1>
                                </td>
                        </tr>
                        <tr>
                            <td style="padding: 40px;">
                                <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333;">Hello {user.name},</p>
                                <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333;">Thank you for registering with MintVerse! To activate your account and gain full access, please verify your email address by clicking the button below:</p>
                                <p style="text-align: center; margin: 30px 0;">
                                    <a href="{verify_url}" style="font-family: sans-serif; display: inline-block; padding: 15px 30px; background-color: #28a745; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">Activate My Account</a>
                                </p>
                                <p style="font-family: sans-serif; font-size: 14px; line-height: 1.6; color: #777; margin-top: 30px;">
                                    If you did not sign up for an account with MintVerse, please disregard this email. No action is required.
                                </p>
                                <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333; margin-top: 40px;">Sincerely,<br>The Team at MintVerse</p>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 20px; background-color: #f0f0f0; border-top: 1px solid #e0e0e0;">
                                <p style="font-family: sans-serif; font-size: 12px; color: #666; margin: 0;">&copy; 2025 MintVerse. All rights reserved.</p>
                                <p style="font-family: sans-serif; font-size: 12px; color: #666; margin: 10px 0 0;">
                                    <a href="[Link to Privacy Policy]" style="color: #007bff; text-decoration: none;">Privacy Policy</a> | <a href="[Link to Terms of Service]" style="color: #007bff; text-decoration: none;">Terms of Service</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    smtp_server = MAIL_SERVER
    smtp_port = int(MAIL_PORT)
    smtp_user = MAIL_USERNAME
    smtp_password = MAIL_PASSWORD
    sender = MAIL_DEFAULT_FROM

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(plain_text)
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)
    return True
