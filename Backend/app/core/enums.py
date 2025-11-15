from enum import Enum


class VendorStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCARDED = "discarded"

