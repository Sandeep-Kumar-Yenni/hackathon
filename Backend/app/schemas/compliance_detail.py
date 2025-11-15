from datetime import date
from typing import Optional

from pydantic import BaseModel, validator


class ComplianceDetailBase(BaseModel):
    tax_identification_number: str
    business_license_number: str
    license_expiry_date: date
    insurance_provider: str
    insurance_policy_number: str
    insurance_expiry_date: date
    industry_certifications: Optional[str] = None
    vendor_id: Optional[int] = None

    @validator("license_expiry_date", "insurance_expiry_date")
    def expiry_in_future(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("expiry dates must be in the future")
        return value


class ComplianceDetailCreate(ComplianceDetailBase):
    pass


class ComplianceDetailRead(ComplianceDetailBase):
    id: int

    class Config:
        from_attributes = True


class ComplianceDetailUpdate(BaseModel):
    tax_identification_number: Optional[str] = None
    business_license_number: Optional[str] = None
    license_expiry_date: Optional[date] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[date] = None
    industry_certifications: Optional[str] = None
    vendor_id: Optional[int] = None

    @validator("license_expiry_date", "insurance_expiry_date")
    def optional_expiry_future(cls, value: Optional[date]) -> Optional[date]:
        if value and value <= date.today():
            raise ValueError("expiry dates must be in the future")
        return value

