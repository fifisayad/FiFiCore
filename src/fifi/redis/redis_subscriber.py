import asyncio
import threading
import orjson
from redis import exceptions as redis_exceptions
from typing import Dict, List, Optional

from ..helpers.get_logger import LoggerFactory
from .redis_client import RedisClient
from ..decorator.log_exception import log_exception

LOGGER = LoggerFactory().get(__name__)


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
        self.redis_client = redis_client
        self.redis = self.redis_client.redis
        self.pubsub = self.redis.pubsub()
        self.channel = channel
        self.messages_lock = threading.Lock()
        self.messages = list()
        # create task for getting messages on the channel
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()

    @classmethod
    async def create(cls, channel: str):
        """create.
        create async method of redis client

        Args:
            channel (str): channel
        """
        redis_client = await RedisClient.create()
        return cls(redis_client, channel)

    def start(self):
        self.loop = asyncio.new_event_loop()

        self.loop.create_task(self.subscriber())
        try:
            self.loop.run_forever()
        finally:
            # Cancel any pending tasks on shutdown
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            self.loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            self.loop.close()
            LOGGER.info("Redis Thread Event loop closed.")

    def close(self):
        """close.
        cancel subscriber future task...
        """
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

    async def close_materials(self) -> None:
        await self.redis_client.close()
        await self.pubsub.aclose()

    @log_exception()
    async def subscriber(self):
        """subscriber.
        it subscribe the channel and also listen to the channel and if there is any message
        it puts on the message buffer.
        """
        while True:
            await self.pubsub.subscribe(self.channel)
            LOGGER.debug("[Subscriber-Redis] Waiting for messages...")
            try:
                async for msg in self.pubsub.listen():
                    try:
                        LOGGER.debug(f"[Subscriber-Redis] Received: {msg}")
                        if msg["type"] == "message":
                            data = orjson.loads(msg["data"])
                            with self.messages_lock:
                                self.messages.append(data)
                            LOGGER.debug(f"[Subscriber-Redis] Received: {data}")
                    except orjson.JSONDecodeError as ex:
                        LOGGER.debug(
                            f"[Subscriber-Redis] Failed to decode message: {str(ex)}"
                        )
            except asyncio.CancelledError:
                LOGGER.error("Task cancelled, exiting gracefully.")
                await self.close_materials()
                raise
            except GeneratorExit:
                LOGGER.error("GeneratorExit: shutting down")
                await self.close_materials()
                raise
            except (
                redis_exceptions.ConnectionError,
                redis_exceptions.TimeoutError,
            ) as e:
                LOGGER.error(f"⚠️ Redis connection lost: {e}. Reconnecting in 3s...")
            except Exception as e:
                LOGGER.error(f"❌ Unexpected error: {e}. Retrying in 5s...")

            # Retry Section for timeout exceptions
            await asyncio.sleep(2)
            self.redis_client = await RedisClient.create()
            self.redis = self.redis_client.redis
            self.pubsub = self.redis.pubsub()

    async def get_messages(self) -> List:
        """get_messages.

        Args:

        Returns:
            List: list of messages on the buffer.
        """
        with self.messages_lock:
            result = self.messages[:]
            self.messages.clear()
        return result

    async def get_last_message(self) -> Optional[Dict]:
        """get_last_message.

        Args:

        Returns:
            Optional[Dict]: return the last message in the buffer
        """
        with self.messages_lock:
            if not self.messages:
                LOGGER.debug(
                    f"[Subscriber-Redis] there is no messages on the {self.channel} channel"
                )
                return None
            result = self.messages[-1]
            self.messages.clear()
        return result
