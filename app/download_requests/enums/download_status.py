from enum import Enum


class DownloadStatus(str, Enum):
    REGISTERED = 'registered'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'