# logger.py

import logging
import sys
import os
from typing import Optional
from utils.config_loader import load_config


def get_logger(
    name: Optional[str] = None, config_path: str = "../configs/app_config.yaml"
) -> logging.Logger:
    """Creates and returns a configured logger.

    Args:
        name (Optional[str]): Name of the logger. Defaults to None for the root logger.
        config_path (str): Path to the logging configuration file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    config = load_config(config_path)
    log_level = config["app"].get("log_level", "INFO").upper()
    logging_config = config.get("logging", {})

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        formatter = logging.Formatter(
            fmt=logging_config.get(
                "formatter", "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
            ),
            datefmt=logging_config.get("datefmt", "%Y-%m-%d %H:%M:%S"),
        )

        # Console Handler
        if logging_config.get("log_to_console", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level, logging.INFO))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File Handler
        if logging_config.get("log_to_file", False):
            log_file_path = logging_config.get("log_file_path", "logs/application.log")
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

            max_bytes = logging_config.get("max_bytes", 0)
            backup_count = logging_config.get("backup_count", 0)

            if max_bytes > 0 and backup_count > 0:
                # Use RotatingFileHandler
                from logging.handlers import RotatingFileHandler

                file_handler = RotatingFileHandler(
                    filename=log_file_path,
                    mode=logging_config.get("log_file_mode", "a"),
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
            else:
                # Use basic FileHandler
                file_handler = logging.FileHandler(
                    filename=log_file_path,
                    mode=logging_config.get("log_file_mode", "a"),
                    encoding="utf-8",
                )

            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
