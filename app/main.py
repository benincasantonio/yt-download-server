from typing import Union

from fastapi import FastAPI
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

from app.services.s3_client import S3Client

from app.download_requests.controllers.v1.routes import router as download_requests_router_v1

# Load environment variables from .env file
load_dotenv()

#s3_client = S3Client()

app = FastAPI()

app.include_router(download_requests_router_v1)


@app.get("/")
def read_root():
    return {"Hello": "World"}


