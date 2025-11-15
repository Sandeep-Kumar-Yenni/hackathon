from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class ComplianceDetail(Base):
    __tablename__ = "compliance_details"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), unique=True, nullable=False)
    tax_identification_number = Column(String, nullable=False)
    business_license_number = Column(String, nullable=False)
    license_expiry_date = Column(Date, nullable=False)
    insurance_provider = Column(String, nullable=False)
    insurance_policy_number = Column(String, nullable=False)
    insurance_expiry_date = Column(Date, nullable=False)
    industry_certifications = Column(Text, nullable=True)

    vendor = relationship("Vendor", back_populates="compliance_detail")

