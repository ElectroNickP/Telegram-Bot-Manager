"""
Domain ports imports for entry points.

This module provides convenient imports for domain ports used by entry points.
"""

from src.core.ports.telegram import TelegramPort
from src.core.ports.storage import ConfigStoragePort
from src.core.ports.updater import AutoUpdaterPort

__all__ = [
    'TelegramPort',
    'ConfigStoragePort', 
    'AutoUpdaterPort'
]
























