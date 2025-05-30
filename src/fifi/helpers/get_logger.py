import logging
import os

from ..decorator.singleton import singleton


@singleton
class GetLogger:
    def __init__(self):
        # Setup logger
        self.LOGGER = logging.getLogger(__name__)
        name_to_level = logging.getLevelNamesMapping()
        level: str = os.getenv("LOG_LEVEL", "INFO")
        logging.basicConfig(level=name_to_level[level])

    def get(self) -> logging.Logger:
        return self.LOGGER
