from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db


router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role(db: Session, role_id: int) -> models.Role:
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RoleRead,
)
def create_role(role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Role)
        .filter(models.Role.name == role_in.name.value)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists",
        )

    role = models.Role(name=role_in.name.value, description=role_in.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("", response_model=list[schemas.RoleRead])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    return roles


@router.get("/{role_id}", response_model=schemas.RoleRead)
def get_role_detail(role_id: int, db: Session = Depends(get_db)):
    return get_role(db, role_id)


@router.put("/{role_id}", response_model=schemas.RoleRead)
def update_role(
    role_id: int, role_in: schemas.RoleUpdate, db: Session = Depends(get_db)
):
    role = get_role(db, role_id)
    if role_in.description is not None:
        role.description = role_in.description
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    # Optional: prevent deleting roles that are in use
    in_use = db.query(models.User).filter(models.User.role_id == role.id).first()
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a role that is assigned to users",
        )
    db.delete(role)
    db.commit()


