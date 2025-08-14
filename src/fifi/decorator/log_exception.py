import functools
import logging
import traceback
from datetime import datetime
import os
from typing import Optional


LOGGER = logging.getLogger(__name__)


def log_exception(root_path: Optional[str] = None):
    """
    Decorator factory that logs exceptions to a file under root_path,
    named as <ClassName>_<method_name>.log.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                self = args[0] if args else None
                class_name = self.__class__.__name__ if self else "NoClass"
                method_name = func.__name__

                if root_path is None:
                    root_dir = "./logs"
                else:
                    root_dir = root_path
                # Ensure directory exists
                os.makedirs(root_dir, exist_ok=True)

                log_file = os.path.join(root_dir, f"{class_name}_{method_name}.log")

                LOGGER.error(f"exception occurred: {traceback.format_exc()}")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now()}] Exception occurred:\n")
                    f.write(traceback.format_exc())
                    f.write("\n")

                raise

        return wrapper

    return decorator
