import asyncio
import threading
import pytest
import time
from multiprocessing import Value, Event
from src.fifi import BaseEngine
from src.fifi import LoggerFactory


LOGGER = LoggerFactory().get(__name__)


# ----------------------------
# Engine classes
# ----------------------------


class MyEngine(BaseEngine):
    name = "test_engine"

    def __init__(self):
        super().__init__()
        self.my_value = 1

    async def prepare(self):
        LOGGER.info(f"preparing....")
        self.my_value = 2
        LOGGER.info(f"preparing.... {self.my_value}")

    async def postpare(self):
        self.my_value = 3
        LOGGER.info(f"postparing ... {self.my_value=}")

    async def execute(self):
        while True:
            await asyncio.sleep(1)


class DummyEngine(BaseEngine):
    name = "dummy_engine"

    def __init__(self, multi_process=False):
        super().__init__(run_in_process=multi_process)
        self.preprocessed = Event()
        self.postprocessed = Event()
        self.counter = Value("i", 0) if multi_process else 0

    async def prepare(self):
        self.preprocessed.set()

    async def execute(self):
        while True:
            if self.run_in_process:
                with self.counter.get_lock():
                    self.counter.value += 1
            else:
                self.counter += 1
            await asyncio.sleep(0.1)

    async def postpare(self):
        self.postprocessed.set()


@pytest.mark.asyncio
class TestBaseEngine:
    test_engine = MyEngine()

    async def test_start_base_engine(self):
        assert self.test_engine.name == "test_engine"
        assert self.test_engine.my_value == 1
        self.test_engine.start()
        await asyncio.sleep(0.5)
        assert self.test_engine.my_value == 2
        is_exist = False
        for thread in threading.enumerate():
            if thread.name == self.test_engine.loop_name:
                LOGGER.info(f"{self.test_engine.loop_name=}")
                is_exist = True
        assert is_exist

    async def test_stop_base_engine(self):
        self.test_engine.stop()
        assert self.test_engine.my_value == 3

    @pytest.mark.parametrize("multi_process", [False, True])
    async def test_engine_lifecycle(self, multi_process):
        LOGGER.info(f"Starting test_engine_lifecycle (multi_process={multi_process})")
        engine = DummyEngine(multi_process=multi_process)

        # start engine
        engine.start()
        await asyncio.sleep(0.5)
        LOGGER.info("Engine started.")
        assert engine.preprocessed.is_set()

        # give it time to run a bit
        time.sleep(1.0)

        # stop engine
        engine.stop()
        LOGGER.info("Engine stopped.")

        # in thread mode, postprocess is set in parent
        if not multi_process:
            assert engine.postprocessed.is_set()
            LOGGER.info("Postprocess verified in thread mode.")
        else:
            assert engine.process is None
            LOGGER.info("Worker stopped in process mode.")
            assert engine.postprocessed.is_set()
            LOGGER.info("Postprocess verified in process mode.")

        # engine did some work
        if multi_process:
            assert engine.counter.value > 0
            LOGGER.info(f"Engine counter={engine.counter.value} verified.")
        else:
            assert engine.counter > 0
            LOGGER.info(f"Engine counter={engine.counter} verified.")
