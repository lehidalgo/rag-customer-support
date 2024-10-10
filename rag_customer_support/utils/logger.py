import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """Creates and returns a configured logger.

    Args:
        name (Optional[str]): Name of the logger. Defaults to None for the root logger.
        level (str): Logging level. Defaults to "INFO".

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Create console handler with the specified log level
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger
