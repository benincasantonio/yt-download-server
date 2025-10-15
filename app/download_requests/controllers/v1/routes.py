from fastapi import APIRouter, HTTPException
import app.config.config as config
from app.download_requests.DTOs.download_request_dto import DownloadRequestDTO
from app.download_requests.repositories.download_request_repository import DownloadRequestRepository
from app.download_requests.schemas.download_request_create_schema import DownloadRequestCreateSchema
from validators import url as validate_url

router = APIRouter(prefix=f"{config.API_BASE_PATH}/v1/download-requests", tags=["Download Requests V1"])

@router.get("/")
async def get_download_requests() -> list[DownloadRequestDTO]:


    download_requests = await DownloadRequestRepository.find_all()
    return DownloadRequestDTO.from_entities(download_requests)

@router.get("/{request_id}")
async def get_download_request(request_id: str) -> DownloadRequestDTO:
    print("id" + request_id)
    download_request = await DownloadRequestRepository.find_by_id(request_id)
    if download_request:
        return DownloadRequestDTO.from_entity(download_request)
    raise HTTPException(status_code=404, detail=f"Download request with id {request_id} not found")

@router.post("/")
async def create_download_request(request: DownloadRequestCreateSchema) -> DownloadRequestDTO:
    if not validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    entity = await DownloadRequestRepository.create(request)
    return DownloadRequestDTO.from_entity(entity)

@router.delete("/{id}")
async def delete_download_request(id: str):
    success = await DownloadRequestRepository.delete(id)
    if success:
        return {"message": f"Download request with id {id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Download request with id {id} not found")

