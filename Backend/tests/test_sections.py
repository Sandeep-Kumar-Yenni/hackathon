import uuid

import pytest

from fastapi import status

from app import models


def _create_vendor(db_session):
    vendor = models.Vendor(
        vendor_name=f"Vendor {uuid.uuid4()}",
        vendor_email=f"{uuid.uuid4()}@vendor.com",
    )
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)
    return vendor.id


@pytest.mark.parametrize(
    "endpoint,payload,update_field,update_value",
    [
        (
            "compliance-details",
            {
                "tax_identification_number": "TAX-001",
                "business_license_number": "LIC-001",
                "license_expiry_date": "2035-01-01",
                "insurance_provider": "InsureCo",
                "insurance_policy_number": "POL-001",
                "insurance_expiry_date": "2035-01-01",
            },
            "insurance_provider",
            "InsureResumed",
        ),
        (
            "banking-details",
            {
                "bank_name": "Bank A",
                "account_holder_name": "Vendor Corp",
                "account_number": "12345678",
                "account_type": "Business",
                "routing_swift_code": "ROUTING",
                "payment_terms": "Net 30",
                "currency": "USD",
            },
            "bank_name",
            "Bank Updated",
        ),
        (
            "contact-details",
            {
                "primary_contact_name": "Jane",
                "job_title": "CFO",
                "email_address": "jane@example.com",
                "phone_number": "+1234567890",
            },
            "primary_contact_name",
            "Janet",
        ),
    ],
)
def test_section_crud(client, db_session, endpoint, payload, update_field, update_value):
    payload["vendor_id"] = _create_vendor(db_session)
    create_resp = client.post(f"/{endpoint}", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    assert created[update_field] == payload[update_field]

    list_resp = client.get(f"/{endpoint}")
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(item["id"] == created["id"] for item in list_resp.json())

    get_resp = client.get(f"/{endpoint}/{created['id']}")
    assert get_resp.status_code == status.HTTP_200_OK

    update_resp = client.put(f"/{endpoint}/{created['id']}", json={update_field: update_value})
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()[update_field] == update_value

    delete_resp = client.delete(f"/{endpoint}/{created['id']}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

