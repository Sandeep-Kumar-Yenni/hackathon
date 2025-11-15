from typing import Optional

from pydantic import BaseModel, Field


class BankingDetailBase(BaseModel):
    bank_name: str
    account_holder_name: str
    account_number: str = Field(..., min_length=8, max_length=18)
    account_type: str
    routing_swift_code: str
    iban: Optional[str] = None
    payment_terms: str
    currency: str
    vendor_id: Optional[int] = None


class BankingDetailCreate(BankingDetailBase):
    pass


class BankingDetailRead(BankingDetailBase):
    id: int

    class Config:
        from_attributes = True


class BankingDetailUpdate(BaseModel):
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = Field(None, min_length=8, max_length=18)
    account_type: Optional[str] = None
    routing_swift_code: Optional[str] = None
    iban: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = None
    vendor_id: Optional[int] = None

