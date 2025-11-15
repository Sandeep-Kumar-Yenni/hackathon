def vendor_payload():
    return {
        "vendor_name": "Vendor X",
        "vendor_email": "vendorx@example.com",
        "contact_person": "Alice",
        "business_details": {
            "legal_business_name": "Vendor X Corp",
            "business_registration_number": "REG-789",
            "business_type": "Private Limited",
            "year_established": 2015,
            "business_address": "456 Vendor Lane",
            "industry_sector": "Procurement",
        },
        "contact_details": {
            "primary_contact_name": "Alice",
            "job_title": "Manager",
            "email_address": "alice@example.com",
            "phone_number": "+19876543210",
        },
        "banking_details": {
            "bank_name": "Vendor Bank",
            "account_holder_name": "Vendor X Corp",
            "account_number": "98765432",
            "account_type": "Business",
            "routing_swift_code": "VENDSWIFT",
            "payment_terms": "Net 45",
            "currency": "GBP",
        },
        "compliance_details": {
            "tax_identification_number": "TAX-789",
            "business_license_number": "LIC-123",
            "license_expiry_date": "2031-01-01",
            "insurance_provider": "VendorIns",
            "insurance_policy_number": "POL-321",
            "insurance_expiry_date": "2031-02-01",
        },
    }


def test_vendor_status_lifecycle(client):
    resp = client.post("/vendors", json=vendor_payload())
    assert resp.status_code == 201
    vendor = resp.json()
    assert vendor["status"] == "active"

    vendor_id = vendor["id"]
    update_resp = client.put(f"/vendors/{vendor_id}", json={"status": "completed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "completed"

    get_resp = client.get(f"/vendors/{vendor_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "completed"

