from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/contact-details", tags=["Contact Details"])


def _get_or_404(detail_id: int, db: Session):
    detail = db.query(models.ContactDetail).filter(models.ContactDetail.id == detail_id).first()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact detail not found")
    return detail


@router.post("", response_model=schemas.ContactDetailRead, status_code=status.HTTP_201_CREATED)
def create_contact_detail(payload: schemas.ContactDetailCreate, db: Session = Depends(get_db)):
    if not payload.vendor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vendor_id is required")
    vendor = (
        db.query(models.Vendor)
        .filter(models.Vendor.id == payload.vendor_id)
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    detail = models.ContactDetail(**payload.model_dump())
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail


@router.get("", response_model=list[schemas.ContactDetailRead])
def list_contact_details(db: Session = Depends(get_db)):
    return db.query(models.ContactDetail).all()


@router.get("/{detail_id}", response_model=schemas.ContactDetailRead)
def get_contact_detail(detail_id: int, db: Session = Depends(get_db)):
    return _get_or_404(detail_id, db)


@router.put("/{detail_id}", response_model=schemas.ContactDetailRead)
def update_contact_detail(detail_id: int, payload: schemas.ContactDetailUpdate, db: Session = Depends(get_db)):
    detail = _get_or_404(detail_id, db)
    updates = payload.dict(exclude_none=True)
    if "vendor_id" in updates:
        vendor = (
            db.query(models.Vendor)
            .filter(models.Vendor.id == updates["vendor_id"])
            .first()
        )
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    for field, value in updates.items():
        setattr(detail, field, value)
    db.commit()
    db.refresh(detail)
    return detail


@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = _get_or_404(detail_id, db)
    db.delete(detail)
    db.commit()

