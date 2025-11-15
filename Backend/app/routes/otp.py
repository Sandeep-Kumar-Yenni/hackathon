import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, HttpUrl
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.email_utils import send_otp_email, send_sns_email

router = APIRouter(prefix="/otp", tags=["OTP & Invitations"])


# In-memory OTP cache: email -> (otp, expires_at_utc)
OTP_TTL_SECONDS = 240  # 4 minutes
otp_cache: dict[str, tuple[str, datetime]] = {}


class OTPRequest(BaseModel):
    email: EmailStr


class OTPResponse(BaseModel):
    detail: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str


class OTPVerifyResponse(BaseModel):
    detail: str


class SNSMailRequest(BaseModel):
    subject: str
    body: str
    # Optional: include a logical recipient to embed in the message body
    email: EmailStr | None = None


class SNSMailResponse(BaseModel):
    detail: str


class InvitationRequest(BaseModel):
    email: EmailStr
    link: HttpUrl  # frontend URL to include in the invitation


class InvitationResponse(BaseModel):
    detail: str


@router.post("", response_model=OTPResponse, status_code=status.HTTP_200_OK)
def send_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    """
    Generate a 6‑digit OTP, store it in in‑memory cache for 2 minutes,
    and send it to the given email address via SNS email.
    """

    # Only send OTPs to vendors that exist in the vendors table
    vendor = (
        db.query(models.Vendor)
        .filter(models.Vendor.vendor_email == payload.email)
        .first()
    )
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not registered as a vendor; OTP not sent.",
        )

    otp = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(seconds=OTP_TTL_SECONDS)
    otp_cache[payload.email.lower()] = (otp, expires_at)

    try:
        send_otp_email(payload.email, otp)
    except Exception as exc:  # pragma: no cover - I/O path
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP email: {exc}",
        ) from exc

    return OTPResponse(detail="OTP sent to recipient email.")


@router.post("/verify", response_model=OTPVerifyResponse, status_code=status.HTTP_200_OK)
def verify_otp(payload: OTPVerifyRequest):
    """
    Verify a 6‑digit OTP for the given email using the in‑memory cache.
    """

    key = payload.email.lower()
    cached = otp_cache.get(key)
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not found or already used.",
        )

    expected_otp, expires_at = cached
    now = datetime.utcnow()

    if now > expires_at:
        # Expired: remove from cache
        otp_cache.pop(key, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired.",
        )

    if payload.otp != expected_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP.",
        )

    # Successful verification: remove OTP so it cannot be reused
    otp_cache.pop(key, None)

    return OTPVerifyResponse(detail="OTP verified successfully.")


@router.post("/send-mail", response_model=SNSMailResponse, status_code=status.HTTP_200_OK)
def send_sns_mail(payload: SNSMailRequest):
    """
    Send a generic email message through the configured AWS SNS topic.

    All email addresses subscribed to the topic will receive this message.
    """

    try:
        send_sns_email(payload.subject, payload.body, payload.email)
    except Exception as exc:  # pragma: no cover - I/O path
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SNS email: {exc}",
        ) from exc

    return SNSMailResponse(detail="Email sent via SNS topic.")


@router.post(
    "/send-invitation",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
)
def send_invitation(payload: InvitationRequest, db: Session = Depends(get_db)):
    """
    Send an invitation link via SNS.

    The provided `link` should be the frontend URL that the user will click.
    """

    # Only send invitations to vendors that exist in the vendors table
    vendor = (
        db.query(models.Vendor)
        .filter(models.Vendor.vendor_email == payload.email)
        .first()
    )
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not registered as a vendor; invitation not sent.",
        )

    subject = "Your Vendor Onboarding Invitation"

    text_body = (
        "You have been invited to complete your vendor onboarding.\n\n"
        f"Please open the following link in your browser:\n{payload.link}\n\n"
        "If you did not expect this invitation, you can ignore this email."
    )

    html_body = f"""
    <html>
      <body>
        <p>You have been invited to complete your vendor onboarding.</p>
        <p>
          Please click the safe link below to continue:<br/>
          <a href="{payload.link}" rel="noopener noreferrer">Continue to Vendor Onboarding</a>
        </p>
        <p>If you did not expect this invitation, you can ignore this email.</p>
      </body>
    </html>
    """

    try:
        # We pass the explicit recipient; SMTP will deliver directly to this address.
        send_sns_email(subject, text_body, payload.email, html_body=html_body)
    except Exception as exc:  # pragma: no cover - I/O path
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invitation email via SNS: {exc}",
        ) from exc

    return InvitationResponse(detail="Invitation email sent via SNS topic.")



