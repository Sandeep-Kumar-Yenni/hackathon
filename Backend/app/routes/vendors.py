from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.core.enums import VendorStatus
from app.database import get_db

router = APIRouter(prefix="/vendors", tags=["Vendor Onboarding"])


def get_vendor(db: Session, vendor_id: int) -> models.Vendor:
    vendor = (
        db.query(models.Vendor)
        .options(
            selectinload(models.Vendor.business_detail),
            selectinload(models.Vendor.contact_detail),
            selectinload(models.Vendor.banking_detail),
            selectinload(models.Vendor.compliance_detail),
        )
        .filter(models.Vendor.id == vendor_id)
        .first()
    )
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


def apply_updates(target, source: dict) -> None:
    for field, value in source.items():
        if value is not None:
            setattr(target, field, value)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.VendorRead,
)
def create_vendor(vendor_in: schemas.VendorCreate, db: Session = Depends(get_db)):
    existing_registration = (
        db.query(models.BusinessDetail)
        .filter(
            models.BusinessDetail.business_registration_number
            == vendor_in.business_details.business_registration_number
        )
        .first()
    )
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business registration number already in use",
        )

    vendor = models.Vendor(
        vendor_name=vendor_in.vendor_name,
        vendor_email=vendor_in.vendor_email,
        contact_person=vendor_in.contact_person,
        contact_number=vendor_in.contact_number,
        vendor_category=vendor_in.vendor_category,
        remarks=vendor_in.remarks,
    )
    vendor.business_detail = models.BusinessDetail(**vendor_in.business_details.model_dump())
    vendor.contact_detail = models.ContactDetail(**vendor_in.contact_details.model_dump())
    vendor.banking_detail = models.BankingDetail(**vendor_in.banking_details.model_dump())
    vendor.compliance_detail = models.ComplianceDetail(**vendor_in.compliance_details.model_dump())

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("", response_model=list[schemas.VendorRead])
def list_vendors(db: Session = Depends(get_db)):
    vendors = (
        db.query(models.Vendor)
        .options(
            selectinload(models.Vendor.business_detail),
            selectinload(models.Vendor.contact_detail),
            selectinload(models.Vendor.banking_detail),
            selectinload(models.Vendor.compliance_detail),
        )
        .all()
    )
    return vendors


@router.get("/comprehensive", response_model=list[schemas.VendorFollowupSummary])
def comprehensive_vendors(db: Session = Depends(get_db)):
    vendors = (
        db.query(models.Vendor)
        .options(
            selectinload(models.Vendor.business_detail),
            selectinload(models.Vendor.contact_detail),
            selectinload(models.Vendor.banking_detail),
            selectinload(models.Vendor.compliance_detail),
            selectinload(models.Vendor.followup_records),
        )
        .all()
    )
    return [
        schemas.VendorFollowupSummary(
            id=vendor.id,
            vendor_name=vendor.vendor_name,
            vendor_email=vendor.vendor_email,
            status=vendor.status,
            onboarding_status=_map_onboarding_status(vendor),
            followups=vendor.followup_records,
        )
        for vendor in vendors
    ]


def _map_onboarding_status(vendor: models.Vendor) -> str:
    if vendor.status == VendorStatus.ACTIVE.value:
        if vendor.followup_records:
            return "Waiting for missing data"
        return "Waiting for vendor response"
    if vendor.status == VendorStatus.COMPLETED.value:
        return "Validated"
    if vendor.status == VendorStatus.DISCARDED.value:
        return "Denied"
    return "Requested"


@router.get("/{vendor_id}", response_model=schemas.VendorRead)
def get_vendor_detail(vendor_id: int, db: Session = Depends(get_db)):
    return get_vendor(db, vendor_id)


@router.put("/{vendor_id}", response_model=schemas.VendorRead)
def update_vendor(vendor_id: int, vendor_in: schemas.VendorUpdate, db: Session = Depends(get_db)):
    vendor = get_vendor(db, vendor_id)

    apply_updates(
        vendor,
        vendor_in.model_dump(
            exclude_none=True,
            exclude={"business_details", "contact_details", "banking_details", "compliance_details"},
        ),
    )

    if vendor_in.business_details:
        business = vendor.business_detail
        if (
            vendor_in.business_details.business_registration_number
            and vendor_in.business_details.business_registration_number
            != business.business_registration_number
        ):
            duplicate = (
                db.query(models.BusinessDetail)
                .filter(
                    models.BusinessDetail.business_registration_number
                    == vendor_in.business_details.business_registration_number
                )
                .first()
            )
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business registration number already in use",
                )
        apply_updates(business, vendor_in.business_details.model_dump(exclude_none=True))

    if vendor_in.contact_details:
        apply_updates(vendor.contact_detail, vendor_in.contact_details.model_dump(exclude_none=True))

    if vendor_in.banking_details:
        apply_updates(vendor.banking_detail, vendor_in.banking_details.model_dump(exclude_none=True))

    if vendor_in.compliance_details:
        apply_updates(vendor.compliance_detail, vendor_in.compliance_details.model_dump(exclude_none=True))

    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = get_vendor(db, vendor_id)
    db.delete(vendor)
    db.commit()

