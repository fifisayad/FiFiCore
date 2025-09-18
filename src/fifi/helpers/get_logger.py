import logging
import coloredlogs
from ..decorator.singleton import singleton


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [%(funcName)s]: %(message)s"

LEVEL_STYLES = {
    "debug": {"color": "cyan"},
    "info": {"color": "green"},
    "warning": {"color": "yellow"},
    "error": {"color": "red"},
    "critical": {"color": "white", "bold": True, "background": "red"},
}

FIELD_STYLES = {
    "asctime": {"color": "magenta"},
    "name": {"color": "blue"},
    "funcName": {"color": "cyan", "bold": True},
}


@singleton
class LoggerFactory:
    def __init__(self, level: str = "INFO"):
        self.level = level.upper()

        # Configure root logger only once
        root_logger = logging.getLogger()
        if not root_logger.hasHandlers():
            coloredlogs.install(
                level=self.level,
                logger=root_logger,
                fmt=LOG_FORMAT,
                datefmt="%H:%M:%S",
                field_styles=FIELD_STYLES,
                level_styles=LEVEL_STYLES,
            )

    def get(self, name: str = __name__) -> logging.Logger:
        return logging.getLogger(name)
