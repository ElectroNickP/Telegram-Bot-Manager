"""
Centralized logging system for plugin-based architecture.
All plugins use this logger - no print() statements.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "bot", log_level: str = None) -> logging.Logger:
    """
    Setup centralized logger for all plugins.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        log_level: Log level from config (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    
    Usage in plugins:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.info(f"[{self.name}] Message received")
    """
    # Get log level from environment or config
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if not exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Format: [2025-10-26 15:30:45] INFO [plugin_name] plugin.py:41 - Message content
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s [%(name)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Rotating file handler (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        logs_dir / "bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger.level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logger.level)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create logger for a module.
    
    Args:
        name: Module name (use __name__)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# Create default bot logger
logger = setup_logger("bot")


