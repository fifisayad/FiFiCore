import time
import logging
from functools import wraps


# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def timeit_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"[{func.__name__}] executed in {duration:.4f} seconds")
        return result

    return wrapper
