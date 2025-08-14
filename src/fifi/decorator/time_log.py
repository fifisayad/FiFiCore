import time
import logging
from functools import wraps


LOGGER = logging.getLogger(__name__)


def timeit_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        LOGGER.info(f"[{func.__name__}] executed in {duration:.4f} seconds")
        return result

    return wrapper
