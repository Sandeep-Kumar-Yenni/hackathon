import smtplib
from email.message import EmailMessage

from pydantic import EmailStr


# SIMPLE SMTP CONFIG (no .env)
# Replace these placeholder strings with your real SMTP details LOCALLY.
SMTP_HOST = "smtp-relay.brevo.com"
SMTP_PORT = 587  # or 465 for SSL
SMTP_USERNAME = "9bab3d001@smtp-brevo.com"
SMTP_PASSWORD = "VnS4cBzDNRL2WHfJ"
FROM_EMAIL = "zamamb@gmail.com"  # or a specific from-address if your provider uses one


def _send_email(subject: str, text_body: str, recipient: EmailStr, html_body: str | None = None) -> None:
    """
    Send an email using plain SMTP with STARTTLS.
    Supports both plain text and optional HTML body.
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = str(recipient)
    msg.set_content(text_body)

    if html_body is not None:
        msg.add_alternative(html_body, subtype="html")

    # STARTTLS-style SMTP (port 587). For SSL on port 465, use smtplib.SMTP_SSL.
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(msg)


def send_otp_email(recipient: EmailStr, otp: str) -> None:
    """
    Send a one‑time password (OTP) email using SMTP.
    The OTP will be highlighted in bold in the HTML version of the email.
    """

    subject = "Your One‑Time Password (OTP)"

    text_body = (
        f"Your verification code is: {otp}\n\n"
        "This code will expire shortly. If you did not request this, you can ignore this email."
    )

    html_body = f"""
    <html>
      <body>
        <p>Your verification code is: <strong>{otp}</strong></p>
        <p>This code will expire shortly. If you did not request this, you can ignore this email.</p>
      </body>
    </html>
    """

    _send_email(subject, text_body, recipient, html_body=html_body)


def send_sns_email(
    subject: str, body: str, recipient: EmailStr | None = None, html_body: str | None = None
) -> None:
    """
    Generic email sender used by the existing endpoints.

    For simplicity this now sends a single email via SMTP instead of SNS.
    The `recipient` must be provided.
    """

    if recipient is None:
        raise RuntimeError("recipient email is required when using SMTP.")

    _send_email(subject, body, recipient, html_body=html_body)

