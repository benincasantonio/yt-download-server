from typing import Optional, Annotated

from beanie import Indexed
from pydantic import Field

from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.base_entity import BaseEntity
from app.download_requests.models.download_request_video import DownloadRequestVideo


class DownloadRequestEntity(BaseEntity):
    url: str
    title: Optional[str] = None
    status: Annotated[DownloadStatus, Indexed()]
    imageUrl: Optional[str] = None
    videos: list[DownloadRequestVideo] = Field(default_factory=list)

    isPlaylist: Optional[bool] = Field(default=False)
    playlistCount: Optional[int] = None
    downloadedCount: Optional[int] = None

    class Settings:
        name = "download_requests"