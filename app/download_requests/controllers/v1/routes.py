from pyexpat.errors import messages

from fastapi import APIRouter, HTTPException
import app.config.config as config
from app.download_requests.DTOs.download_request_dto import DownloadRequestDTO
from app.download_requests.repositories.download_request_repository import DownloadRequestRepository
from app.download_requests.schemas.download_request_create_schema import DownloadRequestCreateSchema

router = APIRouter(prefix=f"{config.API_BASE_PATH}/v1/download-requests", tags=["Download Requests V1"])

@router.get("/")
async def get_download_requests() -> list[DownloadRequestDTO]:
    download_requests = await DownloadRequestRepository.find_all()
    return DownloadRequestDTO.from_entities(download_requests)

@router.get("/{id}")
async def get_download_request(id: str) -> DownloadRequestDTO:
    download_request = await DownloadRequestRepository.find_by_id(id)
    if download_request:
        return DownloadRequestDTO.from_entity(download_request)
    raise HTTPException(status_code=404, detail=f"Download request with id {id} not found")

@router.post("/")
async def create_download_request(request: DownloadRequestCreateSchema) -> DownloadRequestDTO:
    entity = await DownloadRequestRepository.create(request)
    return DownloadRequestDTO.from_entity(entity)

