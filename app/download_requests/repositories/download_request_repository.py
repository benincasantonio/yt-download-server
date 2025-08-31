from collections.abc import Collection

from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.enums.download_status import DownloadStatus


class DownloadRequestRepository:
    @staticmethod
    async def create(data: dict) -> dict:
        # Ensure status is properly converted to enum if it's a string
        status = data.get("status")
        if isinstance(status, str):
            status = DownloadStatus(status)
        elif status is None:
            status = DownloadStatus.REGISTERED  # Default status
            
        entity = DownloadRequestEntity(
            url=data.get("url"),
            status=status,
            image_url=data.get("image_url"),
        )

        await entity.insert()

        return entity.model_dump()