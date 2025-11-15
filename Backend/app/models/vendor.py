from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.enums import VendorStatus
from ..database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(255), nullable=False, index=True)
    vendor_email = Column(String(320), nullable=False, unique=True, index=True)
    status = Column(
        String(32),
        nullable=False,
        default=VendorStatus.ACTIVE.value,
        server_default=VendorStatus.ACTIVE.value,
    )
    contact_person = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    vendor_category = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)

    business_detail = relationship(
        "BusinessDetail",
        back_populates="vendor",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    contact_detail = relationship(
        "ContactDetail",
        back_populates="vendor",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    banking_detail = relationship(
        "BankingDetail",
        back_populates="vendor",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    compliance_detail = relationship(
        "ComplianceDetail",
        back_populates="vendor",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    followup_records = relationship("FollowupRecord", back_populates="vendor", cascade="all, delete-orphan")

