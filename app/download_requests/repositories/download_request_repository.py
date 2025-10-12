from __future__ import annotations

from typing import Optional

from beanie import PydanticObjectId

from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.schemas.download_request_create_schema import DownloadRequestCreateSchema


class DownloadRequestRepository:
    @staticmethod
    async def create(data: DownloadRequestCreateSchema) -> DownloadRequestEntity:
            
        entity = DownloadRequestEntity(
            url=data.url,
            status=DownloadStatus.REGISTERED,
            imageUrl=None
        )

        await entity.insert()

        return entity

    @staticmethod
    async def find_by_id(request_id: str) -> Optional[DownloadRequestEntity]:
        object_id = PydanticObjectId(request_id)
        return await DownloadRequestEntity.find_active(_id=object_id).first_or_none()

    @staticmethod
    async def find_all() -> list[DownloadRequestEntity]:
        return await DownloadRequestEntity.find_active().to_list()

    @staticmethod
    async def update(request_id: str, data: dict) -> Optional[DownloadRequestEntity]:
        entity = await DownloadRequestRepository.find_by_id(request_id)
        if entity:
            for key, value in data.items():
                setattr(entity, key, value)
            await entity.save()
            return entity
        return None

    @staticmethod
    async def delete(request_id: str) -> bool:
        entity = await DownloadRequestRepository.find_by_id(request_id)
        if entity:
            await entity.soft_delete()
            return True
        return False