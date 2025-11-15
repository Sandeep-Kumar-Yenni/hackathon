from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class BusinessDetail(Base):
    __tablename__ = "business_details"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), unique=True, nullable=False)
    legal_business_name = Column(String(255), nullable=False, index=True)
    business_registration_number = Column(String(128), nullable=False, unique=True, index=True)
    business_type = Column(String, nullable=False)
    year_established = Column(Integer, nullable=False)
    business_address = Column(Text, nullable=False)
    number_of_employees = Column(Integer, nullable=True)
    industry_sector = Column(String, nullable=False)

    vendor = relationship("Vendor", back_populates="business_detail")

