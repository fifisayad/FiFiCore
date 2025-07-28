import asyncio
import time
import pytest
import pytest_asyncio

from src.fifi import RedisSubscriber, RedisPublisher
from src.fifi import GetLogger


# TODO: add a test for redis pub-sub time performance
# TOOD: test get messages in the RedisSubscriber

CHANNEL: str = "test_channel"
LOGGER = GetLogger().get()


@pytest_asyncio.fixture
async def setup_redis_subscriber():
    LOGGER.info("Creating Redis Subscriber ....")
    subscriber = await RedisSubscriber.create(CHANNEL)
    yield subscriber
    LOGGER.info("Cleaning Redis Subscriber Task ...")
    subscriber.close()


@pytest.mark.redis
@pytest.mark.asyncio
async def test_create_redis_client(setup_redis_subscriber):
    publisher = await RedisPublisher.create(CHANNEL)
    subscriber = setup_redis_subscriber
    await asyncio.sleep(1)

    test = {"data": "test"}
    await publisher.publish(test)

    await asyncio.sleep(1)
    recieved_test = await subscriber.get_last_message()

    LOGGER.info(f"Recieved Message: {recieved_test}")
    assert test == recieved_test


@pytest.mark.redis
@pytest.mark.asyncio
async def test_performance(setup_redis_subscriber):
    publisher = await RedisPublisher.create(CHANNEL)
    subscriber = setup_redis_subscriber
    await asyncio.sleep(1)

    test = {
        "data": {
            "T": 1681924499999,
            "c": "29258.0",
            "h": "29309.0",
            "i": "15m",
            "l": "29250.0",
            "n": 189,
            "o": "29295.0",
            "s": "BTC",
            "t": 1681923600000,
            "v": "0.98639",
        },
        "time": time.time(),
    }
    await publisher.publish(test)

    await asyncio.sleep(1)
    recieved_test = await subscriber.get_last_message()

    assert test == recieved_test
    circulation_time = time.time() - recieved_test["time"] - 1
    LOGGER.info(f"{circulation_time=}")

    assert circulation_time < 0.1
