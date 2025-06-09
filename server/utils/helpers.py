import re
from flask import flash
import smtplib
from email.message import EmailMessage
from ..config.variables import (
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_SERVER,
    MAIL_DEFAULT_FROM,
)


# Custom password validation function
def validate_password(
    password,
    length_error="Password must be at least 8 characters long.",
    uppercase_error="Password must contain at least one uppercase letter.",
    lowercase_error="Password must contain at least one lowercase letter.",
    digit_error="Password must contain at least one digit.",
    special_error="Password must contain at least one special character.",
):
    # Check length (at least 8 characters)
    if len(password) < 8:
        flash(length_error)
        return length_error
    # Check for at least 1 uppercase letter
    if not re.search(r"[A-Z]", password):
        flash(uppercase_error)
        return uppercase_error
    # Check for at least 1 lowercase letter
    if not re.search(r"[a-z]", password):
        flash(lowercase_error)
        return lowercase_error
    # Check for at least 1 digit
    if not re.search(r"\d", password):
        flash(digit_error)
        return digit_error
    # Check for at least 1 special character (non-alphanumeric)
    if not re.search(r"[!@#$%^&*()_+{}[\]:;<>,.?~]", password):
        flash(special_error)
        return special_error
    return None  # Password meets all requirements


def send_predefined_email(subject, recipient, plain_text, html_content):
    """
    Sends an email using credentials from environment variables.
    """
    smtp_server = MAIL_SERVER
    smtp_port = MAIL_PORT
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
