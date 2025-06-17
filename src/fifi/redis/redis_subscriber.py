import asyncio
import json
from typing import Dict, List, Optional

from ..helpers.get_logger import GetLogger
from .redis_client import RedisClient


class RedisSubscriber:
    """RedisSubscriber.
    this class is subscriber class in terms of getting messages on a channel
    """

    def __init__(self, redis_client: RedisClient, channel: str):
        """__init__.
        in constructor method, it creates a task for subscriber in terms of subscribe a channel
        and try to listen to the channel and get messages

        Args:
            redis_client (RedisClient): redis_client
            channel (str): channel
        """
        self.logger = GetLogger().get()
        self.redis_client = redis_client
        self.redis = self.redis_client.redis
        self.pubsub = self.redis.pubsub()
        self.channel = channel
        self.messages_lock = asyncio.Lock()
        self.messages = list()
        # create task for getting messages on the channel
        self.task = asyncio.create_task(self.subscriber())

    @classmethod
    async def create(cls, channel: str):
        """create.
        create async method of redis client

        Args:
            channel (str): channel
        """
        redis_client = await RedisClient.create()
        return cls(redis_client, channel)
    
    def close(self):
        """close.
        cancel subscriber future task...
        """
        self.task.cancel()

    async def subscriber(self):
        """subscriber.
        it subscribe the channel and also listen to the channel and if there is any message
        it puts on the message buffer.
        """
        await self.pubsub.subscribe(self.channel)
        self.logger.debug("[Subscriber-Redis] Waiting for messages...")
        try:
            async for msg in self.pubsub.listen():
                try:
                    self.logger.debug(f"[Subscriber-Redis] Received: {msg}")
                    if msg["type"] == "message":
                        data = json.loads(msg["data"])
                        async with self.messages_lock:
                            self.messages.append(data)
                        self.logger.debug(f"[Subscriber-Redis] Received: {data}")
                except json.JSONDecodeError:
                    self.logger.debug(
                        f"[Subscriber-Redis] Failed to decode message: {msg}"
                    )
        finally:
            self.logger.debug("[Subscriber-Redis]: finally section ...")
            await self.pubsub.unsubscribe()
            await self.pubsub.punsubscribe()
            await self.redis_client.redis.aclose()
            return

    async def get_messages(self) -> List:
        """get_messages.

        Args:

        Returns:
            List: list of messages on the buffer.
        """
        result = self.messages
        async with self.messages_lock:
            self.messages = []
        return result

    async def get_last_message(self) -> Optional[Dict]:
        """get_last_message.

        Args:

        Returns:
            Optional[Dict]: return the last message in the buffer
        """
        try:
            result = self.messages[-1]
        except IndexError:
            self.logger.warning(
                f"[Subscriber-Redis] there is no messages on the {self.channel} channel"
            )
            return None
        async with self.messages_lock:
            self.messages = []
        return result
