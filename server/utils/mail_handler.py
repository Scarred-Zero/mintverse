import logging
from flask import current_app, url_for
from email.message import EmailMessage
import smtplib

from ..config.variables import (
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_SERVER,
    MAIL_DEFAULT_FROM,
)


def send_verification_code(user):
    """
    Sends a verification email with a code to the user.
    Regenerates the code if expired or missing.
    """
    # Ensure the user has a code (regenerate if needed)
    if hasattr(user, "regenerate_verification_code"):
        user.regenerate_verification_code()
    else:
        # Fallback: generate a random code if method missing
        import random

        user.verification_code = str(random.randint(100000, 999999))
        # You should save the user here if not auto-saved

    try:
        subject = "Verify Your Email - MintVerse"
        recipient = user.email
        plain_text = (
            f"Hello {user.name},\n\n"
            f"Copy the code below and paste to verify your email:\n"
            f"{user.verification_code}\n\n"
            "If you didn't request this, ignore this message."
        )
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
                                    <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333;">Thank you for registering with MintVerse! To activate your account and gain full access, please verify your email address by confirming the verification code:</p>
                                    <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333;">Your verification code is: <b>{user.verification_code}</b></p>
                                    <p style="font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333;">Please copy the code above and paste it in the verification field on our website.</p>
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
                                        <a href="#" style="color: #007bff; text-decoration: none;">Privacy Policy</a> | <a href="#" style="color: #007bff; text-decoration: none;">Terms of Service</a>
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

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = MAIL_DEFAULT_FROM
        msg["To"] = recipient
        msg.set_content(plain_text)
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP_SSL(MAIL_SERVER, int(MAIL_PORT)) as smtp:
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        logging.exception(f"Error sending verification email: {e}")
        print(f"❌ Failed to send verification email: {e}")
        return False
