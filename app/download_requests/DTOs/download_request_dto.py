from typing import Optional
from pydantic import BaseModel, Field
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.models.download_request_video import DownloadRequestVideo
from app.download_requests.enums.download_status import DownloadStatus


class DownloadRequestDTO(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    status: DownloadStatus
    imageUrl: Optional[str] = None
    videos: list[DownloadRequestVideo] = Field(default_factory=list)
    isPlaylist: bool = False
    playlistCount: Optional[int] = None
    downloadedCount: Optional[int] = None

    @classmethod
    def from_entity(cls, entity: DownloadRequestEntity) -> "DownloadRequestDTO":
        return cls(
            id=str(entity.id),  # Convert ObjectId to string
            url=entity.url,
            title=entity.title,
            status=entity.status,  # Pass the enum directly
            imageUrl=entity.imageUrl,
            videos=entity.videos or [],
            isPlaylist=entity.isPlaylist or False,
            playlistCount=entity.playlistCount,
            downloadedCount=entity.downloadedCount,
        )

    @classmethod
    def from_entities(cls, entities: list[DownloadRequestEntity]) -> list["DownloadRequestDTO"]:
        return [cls.from_entity(entity) for entity in entities]
