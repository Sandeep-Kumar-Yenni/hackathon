from datetime import date
from typing import Optional

from pydantic import BaseModel, validator


class BusinessDetailBase(BaseModel):
    legal_business_name: str
    business_registration_number: str
    business_type: str
    year_established: int
    business_address: str
    industry_sector: str
    vendor_id: Optional[int] = None
    number_of_employees: Optional[int] = None

    @validator("year_established")
    def year_must_be_reasonable(cls, value: int) -> int:
        if value < 1800 or value > date.today().year:
            raise ValueError("year_established must be between 1800 and the current year")
        return value


class BusinessDetailCreate(BusinessDetailBase):
    pass


class BusinessDetailRead(BusinessDetailBase):
    id: int

    class Config:
        from_attributes = True


class BusinessDetailUpdate(BaseModel):
    legal_business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    business_type: Optional[str] = None
    year_established: Optional[int] = None
    business_address: Optional[str] = None
    number_of_employees: Optional[int] = None
    industry_sector: Optional[str] = None
    vendor_id: Optional[int] = None

    @validator("year_established")
    def validate_year(cls, value: Optional[int]) -> Optional[int]:
        if value and (value < 1800 or value > date.today().year):
            raise ValueError("year_established must be between 1800 and the current year")
        return value


class BusinessDetailExtractResponse(BusinessDetailBase):
    class Config:
        from_attributes = True

