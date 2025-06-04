import asyncio
import pytest

from src.fifi import RedisSubscriber, RedisPublisher


CHANNEL: str = "test_channel"


@pytest.mark.redis
@pytest.mark.asyncio
async def test_create_redis_client():
    publisher = await RedisPublisher.create(CHANNEL)
    subscriber = await RedisSubscriber.create(CHANNEL)

    test = {"data": "test"}
    await publisher.publish(test)

    await asyncio.sleep(1)
    recieved_test = await subscriber.get_last_message()

    assert test == recieved_test
