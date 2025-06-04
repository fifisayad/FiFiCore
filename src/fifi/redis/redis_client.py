from typing import Any, Dict
import os
import redis.asyncio as aioredis
from redis.asyncio import Redis

from ..decorator.singleton import singleton


class RedisClient:
    """RedisClient.
    This class is going to create redis connection client.
    """

    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    async def create(
        cls,
        host: str = os.getenv("REDIS_HOST", "localhost"),
        port: int = int(os.getenv("REDIS_PORT", 6379)),
        username: str = os.getenv("REDIS_USERNAME", ""),
        password: str = os.getenv("REDIS_PASSWORD", ""),
    ):
        """create.
        this method create a redis client connection
        You can put these input arguments in the .env file and use dotenv
        in order to load .env file for connecting to the Redis.

        Args:
            host (str): host
            port (int): port
            username (str): username
            password (str): password
        """
        kwargs: Dict[str, Any] = {"decode_responses": True}
        if username:
            kwargs["username"] = username
            kwargs["password"] = password
        redis = await aioredis.from_url(f"redis://{host}:{port}", **kwargs)
        return cls(redis)

    async def close(self):
        """close.
        close redis connection
        """
        await self.redis.close()
