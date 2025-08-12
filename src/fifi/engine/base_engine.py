import asyncio
import traceback
import threading
from abc import ABC, abstractmethod
from ..helpers.get_logger import GetLogger


LOGGER = GetLogger().get()


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
    thread_name: str

    def __init__(self):
        """
        Initializes the engine instance by creating a new asyncio event loop
        and setting the thread placeholder to None.
        """
        self.new_loop = asyncio.new_event_loop()
        self.thread = None

    async def start(self):
        """
        Starts the engine by running the `preprocess()` coroutine, launching a new thread
        to host the event loop, and scheduling the `process()` coroutine within that loop.
        """
        LOGGER.info(f"starting {self.name}....")
        await self.preprocess()
        self.thread = threading.Thread(target=self.start_loop)
        self.thread_name = self.thread.name
        self.thread.start()
        asyncio.run_coroutine_threadsafe(self.process(), self.new_loop)

    def start_loop(self):
        """
        Runs the event loop in the current thread.

        This method is intended to be run in a new thread, and will set the thread-local
        event loop and run it until stopped.
        Logs when the loop is stopped.
        """
        asyncio.set_event_loop(self.new_loop)
        try:
            self.new_loop.run_forever()
        except Exception as ex:
            msg_error = traceback.format_exc()
            LOGGER.error(f"engine crash {msg_error}")
        LOGGER.info(
            f"Event loop of engine {self.name} in thread {self.thread_name} stopped"
        )

    @abstractmethod
    async def preprocess(self):
        """
        Coroutine for performing setup tasks before the main engine logic begins.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def process(self):
        """
        Coroutine that contains the main logic of the engine.

        This is the task that runs in the engine's event loop and should
        keep the engine alive as long as it's active.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    async def postprocess(self):
        """
        Coroutine for performing cleanup tasks after the engine is stopped.

        Must be implemented by subclasses.
        """
        pass

    async def stop(self):
        """
        Stops the engine gracefully.

        Calls the `postprocess()` coroutine, schedules the event loop to stop,
        and joins the engine thread to ensure a clean shutdown.
        """
        if self.thread:
            await self.postprocess()
            self.new_loop.call_soon_threadsafe(self.new_loop.stop)
            self.thread.join()
