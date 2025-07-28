import orjson
import traceback
from typing import Dict, Optional
from redis import PubSubError

from ..helpers.get_logger import GetLogger
from .redis_client import RedisClient


class RedisPublisher:
    """RedisPublisher.
    This class manages our publisher on the redis for sending messages to the consumers
    """

    def __init__(self, redis_client: RedisClient, channel: str):
        """__init__.

        Args:
            redis_client (RedisClient): redis_client
            channel (str): channel name
        """
        self.logger = GetLogger().get()
        self.redis_client = redis_client
        self.redis = self.redis_client.redis
        self.channel = channel

    @classmethod
    async def create(cls, channel: str):
        """create.
        this method create an instance of redis client and also the connection to the redis

        Args:
            channel (str): channel
        """
        redis_client = await RedisClient.create()
        return cls(redis_client, channel)

    async def publish(self, message: Optional[Dict]):
        """publish.
        sending a message on the redis channel.

        Args:
            message (Optional[Dict]): message
        """
        publish_message = message
        if type(message) == dict:
            publish_message = orjson.dumps(message)
        try:
            await self.redis.publish(self.channel, publish_message)
            self.logger.debug(
                f"[Publisher-Redis]: published this data: {publish_message} on this channel: {self.channel}"
            )
        except PubSubError:
            error_message = traceback.format_exc()
            self.logger.error(f"[Publisher-Redis] pubsub error: {error_message}")
