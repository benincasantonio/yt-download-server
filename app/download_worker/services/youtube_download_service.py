import asyncio
import logging
from typing import Dict, Any, List
from app.download_requests.enums.download_status import DownloadStatus
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.models.download_request_video import DownloadRequestVideo
from app.download_requests.repositories.download_request_repository import DownloadRequestRepository
import yt_dlp

logger = logging.getLogger(__name__)

class YouTubeDownloadService:

    @staticmethod
    async def download(download_request: DownloadRequestEntity) -> None:
        """
        Main download orchestration method that handles the full lifecycle
        Supports both single videos and playlists
        """
        try:
            # Update status to IN_PROGRESS
            download_request = await DownloadRequestRepository.update(
                str(download_request.id),
                {"status": DownloadStatus.IN_PROGRESS}
            )
            logger.info(f"Processing download request: {download_request.id} - {download_request.url}")

            result = await YouTubeDownloadService._process_download(
                download_request.url,
                str(download_request.id)
            )

            await YouTubeDownloadService._update_download_video_info(result, download_request)



        except Exception as e:
            # Handle any errors and mark as failed
            logger.error(f"Failed to download {download_request.url}: {str(e)}", exc_info=True)
            await DownloadRequestRepository.update(str(download_request.id), {
                "status": DownloadStatus.FAILED
            })

    @staticmethod
    async def _process_download(url: str, request_id: str) -> Dict[str, Any]:
        """
        Execute the actual yt-dlp download in a thread pool to avoid blocking
        Returns dict with file_paths, videos metadata, and playlist info
        """
        def _download():
            downloaded_files = []
            videos_metadata = []

            ydl_opts = {
                'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
                'outtmpl': f'/app/downloads/{request_id}_%(id)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                'keepvideo': False,  # Don't keep intermediate video files after merging
                'postprocessor_args': {
                    'ffmpeg': ['-movflags', 'faststart']  # Optimize for streaming
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)

                is_playlist = 'entries' in info_dict and isinstance(info_dict['entries'], list)

                logger.info('Is playlist: %s', is_playlist)

                print('Is playlist print', is_playlist)


                if is_playlist:
                    # Handle playlist
                    playlist_title = info_dict.get('title', 'Unknown Playlist')
                    playlist_thumbnail = info_dict.get('thumbnail')
                    entries = [e for e in info_dict['entries'] if e is not None]

                    logger.info(f"Processing playlist: {playlist_title} with {len(entries)} videos")

                    for entry in entries:
                        video_id = entry.get('id')
                        ext = entry.get('ext', 'mp4')
                        file_path = f"/app/downloads/{request_id}_{video_id}.{ext}"

                        downloaded_files.append(file_path)
                        videos_metadata.append(DownloadRequestVideo(
                            id=video_id,
                            title=entry.get('title', 'Unknown'),
                            path=file_path,
                            imageUrl=entry.get('thumbnail', ''),
                            duration=entry.get('duration', 0)
                        ))

                    return {
                        'is_playlist': True,
                        'playlist_count': len(entries),
                        'downloaded_count': len(downloaded_files),
                        'playlist_title': playlist_title,
                        'playlist_thumbnail': playlist_thumbnail,
                        'file_paths': downloaded_files,
                        'videos': videos_metadata
                    }
                else:
                    # Handle single video
                    video_id = info_dict.get('id')
                    ext = info_dict.get('ext', 'mp4')
                    file_path = f"/app/downloads/{request_id}_{video_id}.{ext}"

                    video = DownloadRequestVideo(
                        id=video_id,
                        title=info_dict.get('title', 'Unknown'),
                        path=file_path,
                        imageUrl=info_dict.get('thumbnail', ''),
                        duration=info_dict.get('duration', 0)
                    )

                    return {
                        'is_playlist': False,
                        'playlist_count': None,
                        'downloaded_count': 1,
                        'file_paths': [file_path],
                        'videos': [video]
                    }

        # Run in thread pool to avoid blocking async event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _download)


    @staticmethod
    async def _update_download_video_info(result: Dict[str, Any], download_request: DownloadRequestEntity):
        update_data = {
            "status": DownloadStatus.COMPLETED,
            "isPlaylist": result['is_playlist'],
            "videos": [video.model_dump() for video in result['videos']]
        }

        if result['is_playlist']:
            update_data['playlistCount'] = result['playlist_count']
            update_data['downloadedCount'] = result['downloaded_count']
            update_data['title'] = result.get('playlist_title')
            update_data['imageUrl'] = result.get('playlist_thumbnail')
        else:
            if result['videos']:
                update_data['title'] = result['videos'][0].title
                update_data['imageUrl'] = result['videos'][0].imageUrl

        await DownloadRequestRepository.update(str(download_request.id), update_data)

        log_msg = f"Successfully completed download: {download_request.id}"
        if result['is_playlist']:
            log_msg += f" - Playlist with {result['downloadedCount']} videos"
