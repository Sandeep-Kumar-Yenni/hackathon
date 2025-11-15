from typing import List, Optional

from ..core.enums import VendorStatus
from pydantic import BaseModel, EmailStr

from .banking_detail import BankingDetailCreate, BankingDetailRead, BankingDetailUpdate
from .business_detail import BusinessDetailCreate, BusinessDetailRead, BusinessDetailUpdate
from .compliance_detail import (
    ComplianceDetailCreate,
    ComplianceDetailRead,
    ComplianceDetailUpdate,
)
from .contact_detail import (
    ContactDetailCreate,
    ContactDetailRead,
    ContactDetailUpdate,
)
from .followup_record import FollowupRecordRead


class VendorBase(BaseModel):
    vendor_name: str
    vendor_email: EmailStr
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    vendor_category: Optional[str] = None
    remarks: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE


class VendorCreate(VendorBase):
    business_details: BusinessDetailCreate
    contact_details: ContactDetailCreate
    banking_details: BankingDetailCreate
    compliance_details: ComplianceDetailCreate


class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    vendor_category: Optional[str] = None
    remarks: Optional[str] = None
    business_details: Optional[BusinessDetailUpdate] = None
    contact_details: Optional[ContactDetailUpdate] = None
    banking_details: Optional[BankingDetailUpdate] = None
    compliance_details: Optional[ComplianceDetailUpdate] = None
    status: Optional[VendorStatus] = None


class VendorRead(VendorBase):
    id: int
    business_detail: BusinessDetailRead
    contact_detail: ContactDetailRead
    banking_detail: BankingDetailRead
    compliance_detail: ComplianceDetailRead

    class Config:
        from_attributes = True


class VendorFollowupSummary(BaseModel):
    id: int
    vendor_name: str
    vendor_email: EmailStr
    status: VendorStatus
    onboarding_status: str
    followups: List[FollowupRecordRead] = []

    class Config:
        from_attributes = True

