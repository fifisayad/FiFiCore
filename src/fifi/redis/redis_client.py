from typing import Any, Dict
import os
import redis.asyncio as aioredis
from redis.asyncio import Redis


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
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
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
        if not host:
            host = os.getenv("REDIS_HOST", "localhost")
        if not port:
            port = int(os.getenv("REDIS_PORT", 6379))
        if not username:
            username = os.getenv("REDIS_USERNAME", "")
        if not password:
            password = os.getenv("REDIS_PASSWORD", "")

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
