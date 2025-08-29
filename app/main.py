from typing import Union

from fastapi import FastAPI
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

from app.services.s3_client import S3Client

# Load environment variables from .env file
load_dotenv()

s3_client = S3Client()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/yt-video/download")
def download_yt_video(url: str, format: Union[str, None] = None):
    opts = {
        "outtmpl": "%(title)s.%(ext)s",
        "format": format if format else "best",
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return {"status": "downloaded", "title": info.get("title"), "id": info.get("id")}

