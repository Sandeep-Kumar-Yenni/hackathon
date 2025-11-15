from datetime import datetime, timedelta

import uuid

import pytest

from fastapi import status

from app import models
from app.routes import otp as otp_module


def _create_vendor(db_session):
    vendor = models.Vendor(
        vendor_name=f"Vendor {uuid.uuid4()}",
        vendor_email=f"{uuid.uuid4()}@vendor.com",
    )
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)
    return vendor


def test_send_otp_success(client, db_session, monkeypatch):
    vendor = _create_vendor(db_session)
    sent = {}

    def fake_send(email, code):
        sent["email"] = email
        sent["code"] = code

    monkeypatch.setattr(otp_module, "send_otp_email", fake_send)
    resp = client.post("/otp", json={"email": vendor.vendor_email})
    assert resp.status_code == status.HTTP_200_OK
    assert otp_module.otp_cache[vendor.vendor_email.lower()][0] == sent["code"]


def test_verify_otp_success(client):
    email = "verify@example.com"
    otp_module.otp_cache[email.lower()] = ("654321", datetime.utcnow() + timedelta(seconds=120))
    resp = client.post("/otp/verify", json={"email": email, "otp": "654321"})
    assert resp.status_code == status.HTTP_200_OK


def test_verify_otp_invalid(client):
    email = "invalid@example.com"
    otp_module.otp_cache[email.lower()] = ("123456", datetime.utcnow() + timedelta(seconds=120))
    resp = client.post("/otp/verify", json={"email": email, "otp": "000000"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_send_sns_mail(client, db_session, monkeypatch):
    vendor = _create_vendor(db_session)
    sent = {}

    def fake_send(subject, body, recipient, html_body=None):
        sent["recipient"] = recipient

    monkeypatch.setattr(otp_module, "send_sns_email", fake_send)
    resp = client.post("/otp/send-invitation", json={"email": vendor.vendor_email, "link": "https://example.com"})
    assert resp.status_code == status.HTTP_200_OK
    assert sent["recipient"] == vendor.vendor_email

