import time
from functools import wraps
from ..helpers.get_logger import GetLogger


def timeit_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger = GetLogger().get()
        logger.info(f"[{func.__name__}] executed in {duration:.4f} seconds")
        return result

    return wrapper
