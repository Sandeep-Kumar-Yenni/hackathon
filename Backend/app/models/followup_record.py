from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class FollowupRecord(Base):
    __tablename__ = "followup_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    issue_type = Column(String(32), nullable=False)
    followup_status = Column(String(32), nullable=False, default="requested")
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    followup_stage = Column(String(64), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    vendor = relationship("Vendor", back_populates="followup_records")

