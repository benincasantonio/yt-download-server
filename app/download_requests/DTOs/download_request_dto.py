from typing import Optional
from pydantic import BaseModel
from app.download_requests.models.download_request_entity import DownloadRequestEntity


class DownloadRequestDTO(BaseModel):
    id: str
    url: str
    status: str
    image_url: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: DownloadRequestEntity) -> "DownloadRequestDTO":
        return cls(
            id=str(entity.id),  # Convert ObjectId to string
            url=entity.url,
            status=entity.status.value,  # Get the enum value
            image_url=entity.image_url,
        )
    
    @classmethod
    def from_entities(cls, entities: list[DownloadRequestEntity]) -> list["DownloadRequestDTO"]:
        return [cls.from_entity(entity) for entity in entities]
