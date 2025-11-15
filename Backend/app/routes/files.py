from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from azure.storage.blob import BlobServiceClient, ContentSettings


router = APIRouter(prefix="/files", tags=["File Uploads"])


# For simplicity, configure Azure Blob Storage connection in code.
# In a real app, move this to environment variables or configuration.
AZURE_BLOB_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;"
    "AccountName=neocodenexussa;"
    "AccountKey=RfxM0KHdO3cOTX1gP+89S6Ywe/u6Mg5DrSvDznIUxo1YGwunPAHn1fJkgaN/hXa6kcQQeowART1c+AStDu0rnA==;"
    "EndpointSuffix=core.windows.net"
)
DEFAULT_CONTAINER_NAME = "vendorx"


def _get_blob_service_client() -> BlobServiceClient:
    try:
        return BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
    except Exception as exc:  # pragma: no cover - configuration error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Azure Blob client: {exc}",
        ) from exc


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_file_to_blob(
    file: UploadFile = File(...),
):
    """
    Upload a single file to Azure Blob Storage.

    You can test this from Swagger by choosing "multipart/form-data"
    and selecting a file for the `file` field.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    blob_service = _get_blob_service_client()
    container_client = blob_service.get_container_client(DEFAULT_CONTAINER_NAME)

    # Create container if it doesn't exist
    try:
        container_client.create_container()
    except Exception:
        # Ignore if container already exists
        pass

    # Use timestamp + original name to avoid collisions
    safe_name = Path(file.filename).name
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    blob_name = f"{timestamp}_{safe_name}"

    # Infer simple content type from UploadFile
    content_type = file.content_type or "application/octet-stream"

    try:
        data = await file.read()
        container_client.upload_blob(
            name=blob_name,
            data=data,
            overwrite=False,
            content_settings=ContentSettings(content_type=content_type),
        )
    except Exception as exc:  # pragma: no cover - I/O path
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to Azure Blob Storage: {exc}",
        ) from exc

    blob_client = container_client.get_blob_client(blob_name)

    return {
        "filename": safe_name,
        "blob_name": blob_name,
        "url": blob_client.url,
        "content_type": content_type,
        "container": DEFAULT_CONTAINER_NAME,
    }



