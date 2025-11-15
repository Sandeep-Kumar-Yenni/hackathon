import uuid

import pytest

from fastapi import status

from app import models


def _create_vendor_record(db_session):
    vendor = models.Vendor(
        vendor_name="Vendor Test",
        vendor_email=f"{uuid.uuid4()}@example.com",
    )
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)
    return vendor.id


def test_business_detail_crud(client, db_session):
    payload = {
        "legal_business_name": "Test Corp",
        "business_registration_number": "REG-123",
        "business_type": "Private Limited",
        "year_established": 2010,
        "business_address": "123 Test Lane",
        "industry_sector": "IT",
    }
    payload["vendor_id"] = _create_vendor_record(db_session)

    create_resp = client.post("/business-details", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED

    created = create_resp.json()
    assert created["legal_business_name"] == payload["legal_business_name"]
    detail_id = created["id"]

    get_resp = client.get(f"/business-details/{detail_id}")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["business_registration_number"] == payload["business_registration_number"]

    list_resp = client.get("/business-details")
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(item["id"] == detail_id for item in list_resp.json())

    update_payload = {"legal_business_name": "Updated Corp"}
    update_resp = client.put(f"/business-details/{detail_id}", json=update_payload)
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["legal_business_name"] == update_payload["legal_business_name"]

    delete_resp = client.delete(f"/business-details/{detail_id}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT
    missing_resp = client.get(f"/business-details/{detail_id}")
    assert missing_resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "endpoint,payload_key",
    [
        ("contact-details", "primary_contact_name"),
        ("banking-details", "bank_name"),
        ("compliance-details", "tax_identification_number"),
    ],
)
def test_other_section_crud(client, db_session, endpoint, payload_key):
    payload_mapping = {
        "contact-details": {
            "primary_contact_name": "Jane Doe",
            "job_title": "CTO",
            "email_address": "jane@example.com",
            "phone_number": "+1234567890",
        },
        "banking-details": {
            "bank_name": "Test Bank",
            "account_holder_name": "Test Corp",
            "account_number": "12345678",
            "account_type": "Business",
            "routing_swift_code": "TESTSWIFT",
            "payment_terms": "Net 30",
            "currency": "USD",
        },
        "compliance-details": {
            "tax_identification_number": "TAX-123",
            "business_license_number": "LIC-987",
            "license_expiry_date": "2030-01-01",
            "insurance_provider": "InsureCo",
            "insurance_policy_number": "POL-456",
            "insurance_expiry_date": "2030-02-02",
        },
    }

    payload = payload_mapping[endpoint]
    payload["vendor_id"] = _create_vendor_record(db_session)
    create_resp = client.post(f"/{endpoint}", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    identifier = create_resp.json()["id"]
    assert create_resp.json()[payload_key] == payload[payload_key]

    list_resp = client.get(f"/{endpoint}")
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(item["id"] == identifier for item in list_resp.json())

    delete_resp = client.delete(f"/{endpoint}/{identifier}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

