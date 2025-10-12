from pydantic import BaseModel


class DownloadRequestCreateSchema(BaseModel):
    url: str