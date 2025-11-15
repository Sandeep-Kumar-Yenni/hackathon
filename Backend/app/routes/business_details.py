from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/business-details", tags=["Business Details"])


def _get_or_404(detail_id: int, db: Session):
    detail = db.query(models.BusinessDetail).filter(models.BusinessDetail.id == detail_id).first()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business detail not found")
    return detail


@router.post("", response_model=schemas.BusinessDetailRead, status_code=status.HTTP_201_CREATED)
def create_business_detail(payload: schemas.BusinessDetailCreate, db: Session = Depends(get_db)):
    if not payload.vendor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vendor_id is required")
    vendor = (
        db.query(models.Vendor)
        .filter(models.Vendor.id == payload.vendor_id)
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    exists = (
        db.query(models.BusinessDetail)
        .filter(models.BusinessDetail.business_registration_number == payload.business_registration_number)
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Business registration number already exists")
    detail = models.BusinessDetail(**payload.model_dump())
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail


@router.get("", response_model=list[schemas.BusinessDetailRead])
def list_business_details(db: Session = Depends(get_db)):
    return db.query(models.BusinessDetail).all()


@router.get("/{detail_id}", response_model=schemas.BusinessDetailRead)
def get_business_detail(detail_id: int, db: Session = Depends(get_db)):
    return _get_or_404(detail_id, db)


@router.put("/{detail_id}", response_model=schemas.BusinessDetailRead)
def update_business_detail(detail_id: int, payload: schemas.BusinessDetailUpdate, db: Session = Depends(get_db)):
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
def delete_business_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = _get_or_404(detail_id, db)
    db.delete(detail)
    db.commit()

