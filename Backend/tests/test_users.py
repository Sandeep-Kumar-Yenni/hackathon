import uuid

import pytest

from app import models
from app.routes.auth import hash_password
from app.routes.auth import get_current_active_user
from app.schemas.role import RoleName
from app.main import app


def _ensure_role(db_session, name=RoleName.admin.value):
    role = db_session.query(models.Role).filter(models.Role.name == name).first()
    if not role:
        role = models.Role(name=name, description=f"{name} role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
    return role


def _create_user_record(db_session, role):
    user = models.User(
        username=f"user-{uuid.uuid4()}",
        email=f"{uuid.uuid4()}@example.com",
        full_name="Active User",
        password_hash=hash_password("password"),
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(autouse=True)
def override_current_active_user(client, db_session):
    role = _ensure_role(db_session)
    user = _create_user_record(db_session, role)
    app.dependency_overrides[get_current_active_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def _user_payload():
    return {
        "username": f"user-{uuid.uuid4()}",
        "email": f"{uuid.uuid4()}@example.com",
        "full_name": "Test User",
        "password": "supersecret",
        "role": RoleName.admin,
        "is_active": True,
    }


def test_create_user_success(client):
    payload = _user_payload()
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == payload["username"]
    assert data["role"]["name"] == payload["role"].value


def test_create_user_conflict(client):
    payload = _user_payload()
    client.post("/users", json=payload)
    duplicate = client.post("/users", json=payload)
    assert duplicate.status_code == 400


def test_list_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_user_detail(client):
    payload = _user_payload()
    created = client.post("/users", json=payload).json()
    resp = client.get(f"/users/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_update_user_email(client):
    payload = _user_payload()
    created = client.post("/users", json=payload).json()
    new_email = f"{uuid.uuid4()}@example.com"
    resp = client.put(f"/users/{created['id']}", json={"email": new_email})
    assert resp.status_code == 200
    assert resp.json()["email"] == new_email


def test_delete_user(client):
    payload = _user_payload()
    created = client.post("/users", json=payload).json()
    delete_resp = client.delete(f"/users/{created['id']}")
    assert delete_resp.status_code == 204

