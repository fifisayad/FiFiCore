import asyncio
import traceback
import threading
import multiprocessing

from multiprocessing.synchronize import Event
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
    loop_name: str

    def __init__(self, run_in_process: bool = False):
        """
        Initializes the engine instance by creating a new asyncio event loop
        and setting the thread placeholder to None.

        Args:
            run_in_process (bool): If True, run the engine in a multiprocessing.Process
                                instead of a threading.Thread. Defaults to False.
        """
        self.run_in_process = run_in_process
        self.new_loop = asyncio.new_event_loop()
        # can be Thread or Process depending on multi_process flag
        # stop_event only used in process mode
        self.therad = None
        self.processor = None
        self.stop_event = None

    async def start(self):
        """
        Starts the engine by running the `preprocess()` coroutine, launching a new thread
        to host the event loop, and scheduling the `process()` coroutine within that loop.
        """
        LOGGER.info(f"starting {self.name}....")
        await self.preprocess()

        if self.run_in_process:
            self.stop_event = multiprocessing.Event()
            self.processor = multiprocessing.Process(
                target=self.start_process_loop, args=(self.stop_event,)
            )
            self.loop_name = self.processor.name
            self.processor.start()
        else:
            self.thread = threading.Thread(target=self.start_thread_loop)
            self.loop_name = self.thread.name
            self.thread.start()
            asyncio.run_coroutine_threadsafe(self.process(), self.new_loop)

    def start_thread_loop(self):
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
            f"Event loop of engine {self.name} in thread {self.loop_name} stopped"
        )

    def start_process_loop(self, stop_event: Event):
        """
        Runs the event loop in the current thread.

        This method is intended to be run in a new thread, and will set the thread-local
        event loop and run it until stopped.
        Logs when the loop is stopped.
        """
        self.new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.new_loop)

        async def runner():
            # Start main process task
            task = asyncio.create_task(self.process())

            # Wait for stop_event signal
            while not stop_event.is_set():
                await asyncio.sleep(0.2)

            # Stop requested → run postprocess inside child
            await self.postprocess()
            task.cancel()  # cancel main loop if still running
            self.new_loop.stop()

        try:
            self.new_loop.create_task(runner())
            self.new_loop.run_forever()
        except Exception:
            msg_error = traceback.format_exc()
            LOGGER.error(f"engine crash {msg_error}")
        finally:
            LOGGER.info(
                f"Event loop of engine {self.name} in process {self.loop_name} stopped"
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
        await self.stop_process() if self.run_in_process else await self.stop_thread()

    async def stop_process(self):
        """
        Stops the process gracefully.

        Calls the `postprocess()` coroutine, schedules the event loop to stop,
        and joins the engine thread to ensure a clean shutdown.
        """
        if not self.processor:
            return
        # signal process to shut down gracefully by running postprocess()
        # we cant use self.worker.terminate() cause we are running in child process
        # we have to use events to send shutdown signal
        self.stop_event.set()
        self.processor.join()
        self.processor = None
        self.stop_event = None

    async def stop_thread(self):
        if not self.thread:
            return
        # thread mode: run postprocess() here
        await self.postprocess()
        self.new_loop.call_soon_threadsafe(self.new_loop.stop)
        self.thread.join()
        self.thread = None
