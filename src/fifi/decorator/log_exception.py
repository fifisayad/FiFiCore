import functools
import logging
import traceback
import inspect
from datetime import datetime
import os
import re
from typing import Optional


LOGGER = logging.getLogger(__name__)


def _safe_name(s: str) -> str:
    # Keep it filesystem-friendly
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)


def _derive_names(func, args):
    """
    Figure out class and method names, even for static/class methods.
    """
    method_name = getattr(func, "__name__", "unknown")
    class_name = None

    if args:
        receiver = args[0]
        # classmethod: first arg is a class; instance method: first arg is an instance
        if inspect.isclass(receiver):
            class_name = receiver.__name__
        else:
            class_name = receiver.__class__.__name__

    if not class_name:
        # Fall back to qualname: "Class.method" or just "function"
        qn = getattr(func, "__qualname__", "")
        if "." in qn:
            class_name = qn.split(".", 1)[0]
        else:
            class_name = "NoClass"

    return _safe_name(class_name), _safe_name(method_name)


def log_exception(root_path: Optional[str] = None):
    """
    Decorator factory that logs exceptions to a file under `root_path`,
    named `<ClassName>_<method>.log`. Supports sync and async callables.

    Tip for classmethod/staticmethod:
    Put this decorator **closest to the function** (i.e., inside of @classmethod/@staticmethod),
    so it sees the real function:
        @classmethod
        @log_exceptions_to_root("logs")
        def foo(cls): ...
    """
    if root_path is None:
        root_dir = "./logs"
    else:
        root_dir = root_path
    # Ensure directory exists
    os.makedirs(root_dir, exist_ok=True)

    def write_log(log_file, func, args):
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] Exception in '{func.__qualname__}':\n")
            f.write(traceback.format_exc())
            f.write("\n")

    def decorator(func):
        is_coro = inspect.iscoroutinefunction(func)

        if is_coro:

            @functools.wraps(func)
            async def awrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    class_name, method_name = _derive_names(func, args)
                    log_file = os.path.join(root_dir, f"{class_name}_{method_name}.log")
                    LOGGER.error(f"exception occurred: {traceback.format_exc()}")
                    write_log(log_file, func, args)
                    raise

            return awrapper
        else:

            @functools.wraps(func)
            def swrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    class_name, method_name = _derive_names(func, args)
                    log_file = os.path.join(root_dir, f"{class_name}_{method_name}.log")
                    LOGGER.error(f"exception occurred: {traceback.format_exc()}")
                    write_log(log_file, func, args)
                    raise

            return swrapper

    return decorator
