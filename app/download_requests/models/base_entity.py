from abc import ABC
from datetime import datetime, timezone
from typing import Annotated, Optional

from beanie import Document, Indexed, before_event, Insert, Replace
from pydantic import Field


def get_current_utc_time():
    return datetime.now(timezone.utc)


class BaseEntity(ABC, Document):
    """
    Abstract base class that provides common fields for all entity models
    """

    deleted: bool = Field(default=False)
    deletedAt: Optional[datetime] = None
    createdAt: Annotated[datetime, Indexed()] = Field(default_factory=get_current_utc_time)
    updatedAt: datetime = Field(default_factory=get_current_utc_time)

    @before_event(Insert)
    @before_event(Replace)
    def update_timestamps(self):
        self.updatedAt = datetime.now(timezone.utc)

    async def soft_delete(self):
        self.deleted = True
        self.deletedAt = datetime.now(timezone.utc)
        await self.save()

    @classmethod
    def active_entities_query(cls):
        return cls.find(cls.deleted == False)



