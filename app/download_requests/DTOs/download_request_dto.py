from typing import Optional
from pydantic import BaseModel, Field
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.models.download_request_video import DownloadRequestVideo


class DownloadRequestDTO(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    status: str
    image_url: Optional[str] = None
    videos: list[DownloadRequestVideo] = Field(default_factory=list)
    is_playlist: bool = False
    playlist_count: Optional[int] = None
    downloaded_count: Optional[int] = None

    @classmethod
    def from_entity(cls, entity: DownloadRequestEntity) -> "DownloadRequestDTO":
        return cls(
            id=str(entity.id),  # Convert ObjectId to string
            url=entity.url,
            title=entity.title,
            status=entity.status.value,  # Get the enum value
            image_url=entity.image_url,
            videos=entity.videos or [],
            is_playlist=entity.is_playlist or False,
            playlist_count=entity.playlist_count,
            downloaded_count=entity.downloaded_count,
        )

    @classmethod
    def from_entities(cls, entities: list[DownloadRequestEntity]) -> list["DownloadRequestDTO"]:
        return [cls.from_entity(entity) for entity in entities]
