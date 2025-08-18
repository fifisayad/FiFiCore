from aredis_om import HashModel
from typing import Optional
import datetime

from redis.asyncio import Redis

from .redis_client import RedisClient


class RedisBaseModel(HashModel):
    """Base class for Redis OM models."""

    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Meta:
        abstract = True  # Prevents this from being stored directly
        database: Redis

    @classmethod
    async def create(cls, **kwargs):
        """create.
        this method create an instance of redis om model
        """
        redis_client = await RedisClient.create()
        cls.Meta.database = redis_client.redis
        return cls(**kwargs)

    async def save(self, *args, **kwargs):
        """Auto-update timestamps on save."""
        now = datetime.datetime.now(datetime.UTC)
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
        return await super().save(*args, **kwargs)

    async def update(self, **kwargs):
        self.updated_at = datetime.datetime.now(datetime.UTC)
        return await super().update(updated_at=self.updated_at, **kwargs)

    async def delete(self, *args, **kwargs):
        """Remove object from Redis."""
        return await super().delete(pk=self.pk, *args, **kwargs)

    @classmethod
    async def get_by_id(cls, pk: str):
        """Retrieve an object by primary key."""
        return await cls.get(pk)
