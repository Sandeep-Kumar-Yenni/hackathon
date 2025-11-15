from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FollowupRecordBase(BaseModel):
    vendor_id: int
    issue_type: str
    followup_status: str
    subject: str
    body: str
    followup_stage: Optional[str] = None


class FollowupRecordCreate(FollowupRecordBase):
    pass


class FollowupRecordUpdate(BaseModel):
    followup_status: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    followup_stage: Optional[str] = None


class FollowupRecordRead(FollowupRecordBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

