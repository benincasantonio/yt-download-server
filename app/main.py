import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Union

from fastapi import FastAPI
from pymongo import MongoClient
import os
from dotenv import load_dotenv

from app.config.database import init_db
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.repositories.download_request_repository import (
    DownloadRequestRepository,
)
from app.services.s3_client import S3Client

from app.download_requests.controllers.v1.routes import (
    router as download_requests_router_v1,
)

# Load environment variables from .env file
load_dotenv()

# s3_client = S3Client()
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    await DownloadRequestRepository.create(
        {"url": "https://example.com/video.mp4", "status": DownloadStatus.REGISTERED.value}
    )
    print("Database initialized and sample data inserted.")
    yield
    # Shutdown code
    # Close any resources if needed


app = FastAPI(lifespan=lifespan)


app.include_router(download_requests_router_v1)


@app.get("/")
def read_root():
    return {"Hello": "World"}
