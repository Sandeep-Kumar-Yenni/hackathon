from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, constr


class IssueType(str, Enum):
    missing_data = "missing_data"
    incorrect_file = "incorrect_file"
    delayed_response = "delayed_response"
    clarification = "clarification"


class FollowupDraftRequest(BaseModel):
    vendor_name: str
    issue_type: IssueType
    context_notes: Optional[str] = None
    missing_sections: Optional[List[str]] = Field(default=None, alias="missingItems")
    previous_attempts: int = Field(1, ge=1)
    tone: constr(strip_whitespace=True, to_lower=False) = "Polite"


class FollowupDraftResponse(BaseModel):
    subject: str
    body: str
    suggested_signature: str

