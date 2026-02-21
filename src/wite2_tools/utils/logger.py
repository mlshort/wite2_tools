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
import logging
import os
from datetime import datetime

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.paths import LOCAL_LOG_PATH

# 1. Generate the timestamp (e.g., 20260217_1330)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
LOG_FILENAME = f"wite2_{timestamp}.log"

# 2. Define the exact path using os.path.join and your dynamic directory
LOG_PATH = os.path.join(LOCAL_LOG_PATH, LOG_FILENAME)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 3. Configure logging immediately on import
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_PATH, encoding=ENCODING_TYPE),
        logging.StreamHandler()  # Keep printing to console for real-time
                                 # feedback
    ]
)


def get_logger(name):
    """
    Creates or retrieves a logger instance.
    """
    logger = logging.getLogger(name)

    # 1. Prevent double logging by disabling propagation to the root logger
    logger.propagate = False

    # 2. Prevent double-logging by checking if handlers already exist
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(LOG_FORMAT)

        # File Handler
        file_handler = logging.FileHandler(LOG_PATH, encoding=ENCODING_TYPE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler (Keeps terminal output formatted properly)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
