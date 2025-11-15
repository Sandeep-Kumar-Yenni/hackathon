from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class ContactDetail(Base):
    __tablename__ = "contact_details"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), unique=True, nullable=False)
    primary_contact_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    email_address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    secondary_contact_name = Column(String, nullable=True)
    secondary_contact_email = Column(String, nullable=True)
    website = Column(String, nullable=True)

    vendor = relationship("Vendor", back_populates="contact_detail")

