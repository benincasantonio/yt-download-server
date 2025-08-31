from pydantic import BaseModel
from app.download_requests.enums.download_status import DownloadStatus


class DownloadRequestCreateSchema(BaseModel):
    url: str