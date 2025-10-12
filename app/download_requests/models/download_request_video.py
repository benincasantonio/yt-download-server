from typing import Optional
from pydantic import BaseModel


class DownloadRequestVideo(BaseModel):
    id: str
    title: str
    path: str
    image_url: Optional[str] = None
    duration: Optional[int] = 0