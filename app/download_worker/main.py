import asyncio

from app.config.database import init_db
from app.download_requests.enums.download_status import DownloadStatus

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


async def main():
    db = await init_db()
    print("Download worker started")
    await listen_for_download_request_insert(db)

if __name__ == "__main__":
    asyncio.run(main())