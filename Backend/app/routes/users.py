import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.routes.auth import get_current_active_user


router = APIRouter(prefix="/users", tags=["Users"])


def hash_password(password: str) -> str:
    # Simple hash for demo purposes – replace with a stronger algorithm in production
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_role_by_name(db: Session, role_name: schemas.RoleName) -> models.Role:
    role = (
        db.query(models.Role)
        .filter(models.Role.name == role_name.value)
        .first()
    )
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_name.value}' does not exist. "
            "Create it first via /roles or seed default roles.",
        )
    return role


def get_user(db: Session, user_id: int) -> models.User:
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserRead,
)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_username = (
        db.query(models.User)
        .filter(models.User.username == user_in.username)
        .first()
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already in use",
        )

    existing_email = (
        db.query(models.User)
        .filter(models.User.email == user_in.email)
        .first()
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    role = get_role_by_name(db, user_in.role)

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        password_hash=hash_password(user_in.password),
        role_id=role.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    users = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .all()
    )
    return users


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return get_user(db, user_id)


@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    user = get_user(db, user_id)

    # Check for username/email uniqueness if they are changing
    if user_in.username and user_in.username != user.username:
        existing_username = (
            db.query(models.User)
            .filter(models.User.username == user_in.username)
            .first()
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )

    if user_in.email and user_in.email != user.email:
        existing_email = (
            db.query(models.User)
            .filter(models.User.email == user_in.email)
            .first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    if user_in.username is not None:
        user.username = user_in.username
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    if user_in.password:
        user.password_hash = hash_password(user_in.password)

    if user_in.role is not None:
        role = get_role_by_name(db, user_in.role)
        user.role_id = role.id

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()


