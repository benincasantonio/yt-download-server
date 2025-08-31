from abc import ABC
from datetime import datetime, timezone
from typing import Annotated, Optional

from beanie import Document, Indexed, before_event, Insert, Replace
from pydantic import Field


class BaseEntity(ABC, Document):
    """
    Abstract base class that provides common fields for all entity models
    """

    deleted: bool = Field(default=False)
    deletedAt: Optional[datetime] = None
    createdAt: Annotated[datetime, Indexed()] = Field(default=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default=lambda: datetime.now(timezone.utc))

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



