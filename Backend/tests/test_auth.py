import uuid

from fastapi import status

from app import models
from app.routes.auth import hash_password


def _create_role(db_session):
    role = db_session.query(models.Role).filter(models.Role.name == "admin").first()
    if not role:
        role = models.Role(name="admin", description="Admin role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
    return role


def _create_user(db_session, role, password="supersecret"):
    user = models.User(
        username=f"user-{uuid.uuid4()}",
        email=f"{uuid.uuid4()}@example.com",
        full_name="Auth User",
        password_hash=hash_password(password),
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user, password


def test_login_success(client, db_session):
    role = _create_role(db_session)
    user, password = _create_user(db_session, role)
    form = {"username": user.username, "password": password}
    resp = client.post("/auth/token", data=form)
    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in resp.json()


def test_login_invalid_credentials(client, db_session):
    role = _create_role(db_session)
    user, _ = _create_user(db_session, role)
    resp = client.post("/auth/token", data={"username": user.username, "password": "wrong"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

