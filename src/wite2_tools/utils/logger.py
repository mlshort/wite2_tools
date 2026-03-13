"""
Centralized Logging Configuration
=================================

This module initializes and manages the structured logging framework
for the `wite2_tools` package. It ensures that all modules record
their activity to a unified, timestamped log file while simultaneously
providing real-time console feedback.

Core Features:
--------------
* Timestamped Files: Automatically generates a unique log filename
  (e.g., `wite2_20260217_1330.log`) upon initialization, saving all
  session output to the configured logs directory.
* Dual Output: Attaches both `FileHandler` and `StreamHandler` to
  capture persistent debug records alongside user-facing terminal
  output.
* Double-Logging Prevention: The `get_logger` function safely builds
  module-specific logger instances, explicitly preventing propagation
  to the root logger to avoid duplicate log entries.
"""
from logging import Logger
from typing import Final
import logging
import os
import sys
import io
import atexit
from datetime import datetime

# Internal package imports
from wite2_tools.paths import LOCAL_LOG_PATH


# 1. Generate the timestamp (e.g., 20260217_1330)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
LOG_FILENAME = f"wite2_{timestamp}.log"

# 2. Define the exact path
LOG_PATH = os.path.join(LOCAL_LOG_PATH, LOG_FILENAME)
DATE_FORMAT: Final = "%Y-%m-%d %H:%M:%S"
CLEAN_FORMAT: Final = "%(asctime)s - %(levelname)s - %(message)s"
# Modified format to include clickable source code references
DETAILED_FORMAT: Final = '%(asctime)s - %(levelname)s - File "%(pathname)s", ' \
             'line %(lineno)d - %(message)s'
JSON_FORMAT: Final = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "msg": \
              "%(message)s"}'
CSV_FORMAT: Final = "%(asctime)s,%(levelname)s,%(message)s"
MIN_FORMAT: Final = "%(message)s"



# pylint: disable=invalid-name
UTF8_CONSOLE = sys.stdout
if hasattr(sys.stdout, 'buffer'):
    UTF8_CONSOLE = io.TextIOWrapper(sys.stdout.buffer,
                                    encoding='utf-8',
                                    errors='replace')


def get_logger(name: str | None)->Logger:
    """
    Creates or retrieves a logger instance.
    """
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(CLEAN_FORMAT)

        # File Handler
        file_handler = logging.FileHandler(LOG_PATH,
                                           mode='a',
                                           encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler using the global UTF8_CONSOLE stream
        console_handler = logging.StreamHandler(UTF8_CONSOLE)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def set_formatter(msg_format: str)->None:
    new_formatter = logging.Formatter(msg_format, datefmt=DATE_FORMAT)
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(new_formatter)

# Ensure buffers are flushed and files are unlocked when the program/test ends
@atexit.register
def _cleanup_logging() -> None:
    logging.shutdown()
