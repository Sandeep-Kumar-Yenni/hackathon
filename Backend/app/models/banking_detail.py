from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class BankingDetail(Base):
    __tablename__ = "banking_details"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), unique=True, nullable=False)
    bank_name = Column(String, nullable=False)
    account_holder_name = Column(String, nullable=False)
    account_number = Column(String(32), nullable=False, index=True)
    account_type = Column(String, nullable=False)
    routing_swift_code = Column(String, nullable=False)
    iban = Column(String, nullable=True)
    payment_terms = Column(String, nullable=False)
    currency = Column(String, nullable=False)

    vendor = relationship("Vendor", back_populates="banking_detail")

