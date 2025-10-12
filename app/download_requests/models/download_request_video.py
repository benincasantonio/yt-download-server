from typing import Optional
from pydantic import BaseModel


class DownloadRequestVideo(BaseModel):
    id: str
    title: str
    path: str
    imageUrl: Optional[str] = None
    duration: Optional[int] = 0