import asyncio
import logging
from typing import Dict, Any
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.repositories.download_request_repository import DownloadRequestRepository
import yt_dlp

logger = logging.getLogger(__name__)

class YouTubeDownloadService:

    @staticmethod
    async def download(download_request: DownloadRequestEntity) -> None:
        """
        Main download orchestration method that handles the full lifecycle
        """
        try:
            # Update status to IN_PROGRESS
            download_request = await DownloadRequestRepository.update(
                str(download_request.id),
                {"status": DownloadStatus.IN_PROGRESS}
            )
            logger.info(f"Processing download request: {download_request.id} - {download_request.url}")

            # Extract video info and download
            info, file_path = await YouTubeDownloadService._process_download(
                download_request.url,
                str(download_request.id)
            )

            # Update entity with success data
            await DownloadRequestRepository.update(str(download_request.id), {
                "status": DownloadStatus.COMPLETED,
                "downloadPaths": [file_path],
                "image_url": info.get('thumbnail')
            })
            logger.info(f"Successfully completed download: {download_request.id} -> {file_path}")

        except Exception as e:
            # Handle any errors and mark as failed
            logger.error(f"Failed to download {download_request.url}: {str(e)}", exc_info=True)
            await DownloadRequestRepository.update(str(download_request.id), {
                "status": DownloadStatus.FAILED
            })

    @staticmethod
    async def _process_download(url: str, request_id: str) -> tuple[Dict[str, Any], str]:
        """
        Execute the actual yt-dlp download in a thread pool to avoid blocking
        Returns: (info_dict, final_file_path)
        """
        def _download():
            ydl_opts = {
                'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
                'outtmpl': f'/app/downloads/{request_id}_%(id)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                # Get actual file extension from info
                ext = info_dict.get('ext', 'mp4')
                file_path = f"/app/downloads/{request_id}_{info_dict['id']}.{ext}"
                return info_dict, file_path

        # Run in thread pool to avoid blocking async event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)
