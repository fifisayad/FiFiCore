import asyncio
import threading
import pytest

from src.fifi import BaseEngine
from src.fifi import GetLogger


LOGGER = GetLogger().get()


class MyEngine(BaseEngine):
    name = "test_engine"

    def __init__(self):
        super().__init__()
        self.my_value = 1

    async def preprocess(self):
        self.my_value = 2

    async def postprocess(self):
        self.my_value = 3
        LOGGER.info(f"postprocess {self.my_value=}")

    async def process(self):
        while True:
            await asyncio.sleep(1)


@pytest.mark.asyncio
class TestBaseEngine:
    test_engine = MyEngine()

    async def test_start_base_engine(self):
        assert self.test_engine.name == "test_engine"
        assert self.test_engine.my_value == 1
        await self.test_engine.start()
        assert self.test_engine.my_value == 2
        is_exist = False
        for thread in threading.enumerate():
            if thread.name == self.test_engine.thread_name:
                LOGGER.info(f"{self.test_engine.thread_name=}")
                is_exist = True
        assert is_exist

    async def test_stop_base_engine(self):
        await self.test_engine.stop()
        assert self.test_engine.my_value == 3
