"""
small, dependency-free helper functions shared across the personio_py package
"""

import logging

logger = logging.getLogger("personio_py")

_unique_logs = set()


def log_once(level: int, message: str):
    """Log a message only the first time it is seen, to avoid spamming the log."""
    if message not in _unique_logs:
        logger.log(level, message)
        _unique_logs.add(message)
