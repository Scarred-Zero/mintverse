import re
from flask import flash, jsonify, request
import smtplib
from email.message import EmailMessage


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


def contact():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    msg = EmailMessage()
    msg["Subject"] = f"Contact from {name}"
    msg["From"] = email
    msg["To"] = "reginanostraschools@gmail.com"
    msg["Reply-To"] = email

    # Plain text fallback
    msg.set_content(f"Name: {name}\nEmail: {email}\nMessage: {message}")

    # Improved HTML template
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #f9f9f9; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 32px;">
          <div style="text-align: center; margin-bottom: 24px;">
            From Mintverse NFT Website</p>
          </div>
          <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
          <table style="width: 100%; font-size: 16px;">
            <tr>
              <td style="padding: 8px 0; color: #2a5298; font-weight: bold;">Name:</td>
              <td style="padding: 8px 0;">{name}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #2a5298; font-weight: bold;">Email:</td>
              <td style="padding: 8px 0;">{email}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #2a5298; font-weight: bold; vertical-align: top;">Message:</td>
              <td style="padding: 8px 0; white-space: pre-line;">{message}</td>
            </tr>
          </table>
          <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
          <div style="text-align: center; color: #aaa; font-size: 13px;">
            MintVerse &copy; {2025}
          </div>
        </div>
      </body>
    </html>
    """
    msg.add_alternative(html_content, subtype="html")

    # Use your SMTP server details here
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    #     smtp.login("support@mintverse.art", "hcxv nwpg vnqk jvhv")
    #     smtp.send_message(msg)

    return jsonify({"status": "success"})


def send_dynamic_mail(
    subject,
    recipient,
    sender,
    plain_text,
    html_content,
    smtp_user,
    smtp_password,
    smtp_server="smtp.gmail.com",
    smtp_port=465,
):
    """
    Utility to send an email with dynamic HTML template.
    """
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
