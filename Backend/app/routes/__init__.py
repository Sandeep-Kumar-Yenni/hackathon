from .business_details import router as business_details_router
from .banking_details import router as banking_details_router
from .compliance_details import router as compliance_details_router
from .contact_details import router as contact_details_router
from .vendors import router as vendor_router
from .otp import router as otp_router
from .roles import router as role_router
from .users import router as user_router
from .auth import router as auth_router
from .files import router as file_router
from .followups import router as followups_router
from .followup_records import router as followup_records_router

__all__ = [
    "business_details_router",
    "banking_details_router",
    "compliance_details_router",
    "contact_details_router",
    "followup_records_router",
    "followups_router",
    "vendor_router",
    "otp_router",
    "role_router",
    "user_router",
    "auth_router",
    "file_router"
]

