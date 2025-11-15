import uuid

import pytest

from fastapi import status

from app import models


def _create_role_payload(name: str = None):
    return {
        "name": name or "admin",
        "description": "Test description",
    }


def test_create_and_retrieve_role(client):
    payload = _create_role_payload()
    create_resp = client.post("/roles", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    assert created["description"] == payload["description"]

    detail_resp = client.get(f"/roles/{created['id']}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == created["id"]


def test_list_roles(client):
    payload = _create_role_payload()
    client.post("/roles", json=payload)
    resp = client.get("/roles")
    assert resp.status_code == status.HTTP_200_OK
    assert any(item["name"] == payload["name"] for item in resp.json())


def test_create_role_duplicate(client):
    payload = _create_role_payload("vendor")
    first = client.post("/roles", json=payload)
    assert first.status_code == status.HTTP_201_CREATED
    duplicate = client.post("/roles", json=payload)
    assert duplicate.status_code == status.HTTP_400_BAD_REQUEST


def test_update_role_description(client):
    payload = _create_role_payload()
    role = client.post("/roles", json=payload).json()
    update_resp = client.put(
        f"/roles/{role['id']}",
        json={"description": "Updated description"},
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["description"] == "Updated description"


def test_delete_role(client, db_session):
    payload = _create_role_payload()
    role_id = client.post("/roles", json=payload).json()["id"]
    delete_resp = client.delete(f"/roles/{role_id}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT


def test_delete_role_in_use(client, db_session):
    role_payload = _create_role_payload()
    role_id = client.post("/roles", json=role_payload).json()["id"]
    user = models.User(
        username=f"user-{uuid.uuid4()}",
        email=f"{uuid.uuid4()}@example.com",
        full_name="In Use",
        password_hash="hash",
        role_id=role_id,
    )
    db_session.add(user)
    db_session.commit()

    delete_resp = client.delete(f"/roles/{role_id}")
    assert delete_resp.status_code == status.HTTP_400_BAD_REQUEST

