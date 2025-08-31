import logging
import os

from pymongo import AsyncMongoClient, MongoClient
from beanie import init_beanie

from app.download_requests.models.download_request_entity import DownloadRequestEntity


async def init_db():
    print(os.getenv("MONGO_URI"))
    client = AsyncMongoClient(
        os.getenv("MONGO_URI"),
        username=os.getenv("MONGO_ROOT_USERNAME"),
        password=os.getenv("MONGO_ROOT_PASSWORD"),
    )

    db = client["yt_downloads"]


    await init_beanie(database=db, document_models=[DownloadRequestEntity])
    logging.info("Connected to MongoDB")
