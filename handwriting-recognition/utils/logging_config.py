"""Logging setup for Pen2Pixel.

Logging is configured from the application configuration rather than hard-coded.
The setup is idempotent: calling it again replaces handlers instead of
accumulating duplicate log lines.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from config.loader import get_path

LOGGER_NAME = "pen2pixel"


def configure_logging(config: Mapping[str, Any]) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        config: Validated Pen2Pixel configuration.

    Returns:
        The configured logger.

    Raises:
        ValueError: If the configured log level is invalid.
        OSError: If a file handler cannot be created.
    """
    settings = config["logging"]
    level_name = str(settings["level"]).upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        raise ValueError(f"Invalid logging level: {settings['level']!r}")

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(settings["format"])

    if settings.get("console_enabled", True):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    if settings.get("file_enabled", False):
        log_dir = get_path(config, "paths.log_dir")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / settings["file_name"], encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
