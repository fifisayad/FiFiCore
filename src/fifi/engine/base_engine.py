import asyncio
import signal
import time
import threading
import multiprocessing

from abc import ABC, abstractmethod
from ..helpers.get_logger import LoggerFactory


LOGGER = LoggerFactory().get(__name__)

keyboard_interrupt = False


def handle_signal(signum, frame):
    global keyboard_interrupt
    print(f"Received signal {signum}, shutting down gracefully...")
    keyboard_interrupt = True


class BaseEngine(ABC):
    """
    Abstract base class for a threaded asynchronous engine using its own event loop.

    This class provides a structured lifecycle for a engine that runs an asyncio event loop
    in a separate thread. Subclasses must implement the `preprocess`, `process`, and
    `postprocess` asynchronous methods to define their behavior.

    Attributes:
        name (str): The name of the engine.
        thread_name (str): Name of the thread running the event loop.
        new_loop (asyncio.AbstractEventLoop): The asyncio event loop for this engine.
        thread (Optional[threading.Thread]): The thread in which the event loop runs.
    """

    name: str
    loop_name: str

    def __init__(self, run_in_process: bool = False, catch_interrupt: bool = True):
        """
        Initializes the engine instance by creating a new asyncio event loop
        and setting the thread placeholder to None.

        Args:
            run_in_process (bool): If True, run the engine in a multiprocessing.Process
                                instead of a threading.Thread. Defaults to False.
        """
        self.run_in_process = run_in_process
        self.catch_interrupt = catch_interrupt
        self.therad = None
        self.process = None
        self.stop_event = None
        self.shutdowned = None
        self.pipeline_task = None

    def start(self):
        """
        Starts the engine by running the `preprocess()` coroutine, launching a new thread
        to host the event loop, and scheduling the `process()` coroutine within that loop.
        """
        LOGGER.info(f"starting {self.name}....")
        if self.run_in_process:
            self.stop_event = multiprocessing.Event()
            self.shutdowned = multiprocessing.Event()
            self.process = multiprocessing.Process(
                target=self.start_loop, name=self.name
            )
            self.loop_name = self.process.name
            self.process.start()
        else:
            self.stop_event = threading.Event()
            self.shutdowned = threading.Event()
            self.thread = threading.Thread(target=self.start_loop, name=self.name)
            self.loop_name = self.thread.name
            self.thread.start()

    def start_loop(self):
        if self.process is not None:
            # Register handlers for SIGTERM (docker stop) and SIGINT (Ctrl+C)
            signal.signal(signal.SIGTERM, handle_signal)
            signal.signal(signal.SIGINT, handle_signal)

        self.new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.new_loop)

        async def runner() -> None:
            # Start main process task
            self.pipeline_task = asyncio.create_task(self.pipeline())

            # Wait for stop_process_event signal
            while self.stop_event and not self.stop_event.is_set():
                await asyncio.sleep(0.2)
                if self.catch_interrupt and keyboard_interrupt:
                    break

            self.pipeline_task.cancel()  # cancel main loop if still running
            try:
                await self.pipeline_task
            except asyncio.CancelledError:
                LOGGER.critical(f"{self.name}: process pipeline canceled")
            self.new_loop.stop()

        self.new_loop.create_task(runner())
        self.new_loop.run_forever()
        LOGGER.info(f"Event loop of engine {self.name} in {self.loop_name} stopped")

    async def pipeline(self):
        LOGGER.info(f"preparing {self.name}....")
        await self.prepare()
        try:
            LOGGER.info(f"executing {self.name}....")
            await self.execute()
        finally:
            LOGGER.info(f"postparing {self.name}....")
            await self.postpare()
            if self.shutdowned:
                self.shutdowned.set()

    @abstractmethod
    async def prepare(self):
        """
        Coroutine for performing setup tasks before the main engine logic begins.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def execute(self):
        """
        Coroutine that contains the main logic of the engine.

        This is the task that runs in the engine's event loop and should
        keep the engine alive as long as it's active.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def postpare(self):
        """
        Coroutine for performing cleanup tasks after the engine is stopped.

        Must be implemented by subclasses.
        """
        pass

    def stop(self):
        """
        Stops the engine gracefully.

        Calls the `postprocess()` coroutine, schedules the event loop to stop,
        and joins the engine thread to ensure a clean shutdown.
        """
        self.stop_process() if self.run_in_process else self.stop_thread()

    def stop_process(self):
        if not self.process or not self.stop_event:
            return

        if self.shutdowned and self.shutdowned.is_set():
            LOGGER.critical(f"{self.name}: it's already shutdowned")
            self.process = None
            self.stop_event = None
            return
        self.stop_event.set()
        while self.shutdowned and not self.shutdowned.is_set():
            time.sleep(0.5)
        self.process.terminate()
        self.process.join()
        self.process = None
        self.stop_event = None

    def stop_thread(self):
        if not self.thread or not self.pipeline_task or not self.stop_event:
            return
        if self.shutdowned and self.shutdowned.is_set():
            LOGGER.critical(f"{self.name}: it's already shutdowned")
            self.thread = None
            self.stop_event = None
            return
        self.stop_event.set()
        while self.shutdowned and not self.shutdowned.is_set():
            time.sleep(0.5)
        self.thread.join()
        self.thread = None
