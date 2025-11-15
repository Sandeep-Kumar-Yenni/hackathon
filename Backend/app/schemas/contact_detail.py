from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class ContactDetailBase(BaseModel):
    primary_contact_name: str
    job_title: str
    email_address: EmailStr
    phone_number: str
    vendor_id: Optional[int] = None
    secondary_contact_name: Optional[str] = None
    secondary_contact_email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None


class ContactDetailCreate(ContactDetailBase):
    pass


class ContactDetailRead(ContactDetailBase):
    id: int

    class Config:
        from_attributes = True


class ContactDetailUpdate(BaseModel):
    primary_contact_name: Optional[str] = None
    job_title: Optional[str] = None
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    secondary_contact_name: Optional[str] = None
    secondary_contact_email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    vendor_id: Optional[int] = None

