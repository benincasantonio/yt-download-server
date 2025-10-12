from enum import Enum


class DownloadStatus(str, Enum):
    REGISTERED = 'Registered'
    IN_PROGRESS = 'InProgress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'