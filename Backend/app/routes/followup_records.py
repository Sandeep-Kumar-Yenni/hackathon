from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/followup-records", tags=["Followup Records"])


def _get_record(record_id: int, db: Session) -> models.FollowupRecord:
    record = (
        db.query(models.FollowupRecord)
        .options(selectinload(models.FollowupRecord.vendor))
        .filter(models.FollowupRecord.id == record_id)
        .first()
    )
    if not record or record.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up record not found")
    return record


@router.post("", response_model=schemas.FollowupRecordRead, status_code=status.HTTP_201_CREATED)
def create_followup_record(payload: schemas.FollowupRecordCreate, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == payload.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    record = models.FollowupRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[schemas.FollowupRecordRead])
def list_followup_records(
    vendor_id: int | None = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(models.FollowupRecord).options(selectinload(models.FollowupRecord.vendor))
    if vendor_id is not None:
        query = query.filter(models.FollowupRecord.vendor_id == vendor_id)
    if not include_deleted:
        query = query.filter(models.FollowupRecord.is_deleted == False)  # noqa: E712
    return query.all()


@router.get("/{record_id}", response_model=schemas.FollowupRecordRead)
def get_followup_record(record_id: int, db: Session = Depends(get_db)):
    return _get_record(record_id, db)


@router.put("/{record_id}", response_model=schemas.FollowupRecordRead)
def update_followup_record(record_id: int, payload: schemas.FollowupRecordUpdate, db: Session = Depends(get_db)):
    record = _get_record(record_id, db)
    updates = payload.dict(exclude_none=True)
    for field, value in updates.items():
        setattr(record, field, value)
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_followup_record(record_id: int, db: Session = Depends(get_db)):
    record = _get_record(record_id, db)
    record.is_deleted = True
    record.updated_at = datetime.utcnow()
    db.commit()

