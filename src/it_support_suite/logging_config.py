"""Privacy-conscious application logging and crash reporting."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import traceback

APP_NAME = "ITSupportToolSuite"


def log_directory() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return base / APP_NAME / "logs"


def configure_logging() -> Path:
    directory = log_directory()
    directory.mkdir(parents=True, exist_ok=True)
    log_file = directory / "application.log"
    root = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        handler = RotatingFileHandler(
            log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        ))
        root.addHandler(handler)
        root.setLevel(logging.INFO)
    return log_file


def install_exception_hook() -> None:
    logger = logging.getLogger("crash")

    def handle(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical(
            "Unhandled exception\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )

    sys.excepthook = handle
