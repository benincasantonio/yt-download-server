from collections.abc import Collection

from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.schemas.download_request_create_schema import DownloadRequestCreateSchema


class DownloadRequestRepository:
    @staticmethod
    async def create(data: DownloadRequestCreateSchema) -> DownloadRequestEntity:
            
        entity = DownloadRequestEntity(
            url=data.url,
            status=DownloadStatus.REGISTERED,
            image_url=None
        )

        await entity.insert()

        return entity

    @staticmethod
    async def find_by_id(request_id: str) -> DownloadRequestEntity | None:
        return await DownloadRequestEntity.get(request_id)

    @staticmethod
    async def find_all() -> list[DownloadRequestEntity]:
        return await DownloadRequestEntity.find().to_list()

    @staticmethod
    async def update(request_id: str, data: dict) -> DownloadRequestEntity | None:
        entity = await DownloadRequestEntity.get(request_id)
        if entity:
            entity.update(**data)
            await entity.save()
            return entity
        return None