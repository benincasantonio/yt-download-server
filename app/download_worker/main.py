import asyncio

from app.config.database import init_db
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_worker.services.youtube_download_service import YouTubeDownloadService


async def listen_for_download_request_insert(db):
    pipeline = [
        {
            "$match": {
                "operationType": "insert",
                "fullDocument.status": DownloadStatus.REGISTERED.value,
                "fullDocument.deleted": False,
            }
        }
    ]

    stream = await db["download_requests"].watch(pipeline)

    async for change in stream:
        print("📥 New request to download:", change["fullDocument"])
        download_request = DownloadRequestEntity(**change["fullDocument"])
        await YouTubeDownloadService.download(download_request)





async def main():
    db = await init_db()
    print("Download worker started")
    await listen_for_download_request_insert(db)

if __name__ == "__main__":
    asyncio.run(main())