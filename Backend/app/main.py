import uvicorn
import os
import sys
from fastapi import FastAPI

# Ensure the parent directory (containing the `app` package) is on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.database import Base, engine  # type: ignore  # noqa: E402
from app.routes import (
    auth_router,
    banking_details_router,
    business_details_router,
    compliance_details_router,
    contact_details_router,
    followup_records_router,
    followups_router,
    otp_router,
    role_router,
    user_router,
    vendor_router,
    files
)

try:
    from .database import Base, engine
    from .routes import (
        auth_router,
        banking_details_router,
        business_details_router,
        compliance_details_router,
        contact_details_router,
        followup_records_router,
        followups_router,
        otp_router,
        role_router,
        user_router,
        vendor_router,
    )
except ImportError:  # allow script execution
    from app.database import Base, engine
    from app.routes import (
        auth_router,
        banking_details_router,
        business_details_router,
        compliance_details_router,
        contact_details_router,
        followups_router,
        otp_router,
        role_router,
        user_router,
        vendor_router,
    )


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vendor Onboarding API",
    description=(
        "Capture vendor details, contact information, banking data, compliance records, "
        "and manage users and roles for procurement onboarding."
    ),
    version="0.2.0",
)

app.include_router(vendor_router)
app.include_router(otp_router)
app.include_router(role_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(followups_router)
app.include_router(followup_records_router)
app.include_router(business_details_router)
app.include_router(contact_details_router)
app.include_router(banking_details_router)
app.include_router(compliance_details_router)


@app.get("/", tags=["root"])
def health_check():
    return {"status": "ok", "message": "Vendor onboarding API is running"}


def init_app(host: str = "127.0.0.1", port: int = 8080, reload: bool = False) -> None:
    """Run the application via Uvicorn."""
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    init_app()

