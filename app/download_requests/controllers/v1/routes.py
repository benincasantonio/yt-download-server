from pyexpat.errors import messages

from fastapi import APIRouter
import app.config.config as config

router = APIRouter(prefix=f"{config.API_BASE_PATH}/v1/download-requests", tags=["Download Requests V1"])

@router.get("/")
async def get_download_requests():
    return {"message": "List of download requests"}

@router.get("/{id}")
async def get_download_request(id: str):
    message = f"Download request with {id} retrieved"
    return {"message": message}

@router.post("/")
async def create_download_request():
    return {"message": "Download request created"}

