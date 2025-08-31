from typing import Optional, Annotated

from beanie import Indexed
from pydantic import Field

from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.base_entity import BaseEntity


class DownloadRequestEntity(BaseEntity):
    url: str
    status: Annotated[DownloadStatus, Indexed()]
    image_url: Optional[str] = None
    downloadPaths: Optional[list[str]] = Field(default_factory=list)

    class Settings:
        name = "download_requests"