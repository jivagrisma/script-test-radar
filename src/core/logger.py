"""
Logging configuration for test-radar.
Provides rich console output and file logging with color support.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union

import colorlog
from rich.console import Console
from rich.logging import RichHandler

# Constants
DEFAULT_LOG_FORMAT = "%(log_color)s%(levelname)-8s%(reset)s %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

class RadarLogger:
    """Custom logger for test-radar"""
    
    def __init__(
        self,
        name: str = "test-radar",
        level: str = "INFO",
        log_file: Optional[Union[str, Path]] = None,
        console: bool = True
    ):
        """Initialize logger
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional path to log file
            console: Whether to enable console output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        if console:
            self._setup_console_handler()
            
        if log_file:
            self._setup_file_handler(log_file)
    
    def _setup_console_handler(self) -> None:
        """Setup rich console handler with colors"""
        console = Console()
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            enable_link_path=True
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
    
    def _setup_file_handler(self, log_file: Union[str, Path]) -> None:
        """Setup file handler with color support
        
        Args:
            log_file: Path to log file
        """
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = colorlog.StreamHandler(open(log_file, 'a'))
        handler.setFormatter(
            colorlog.ColoredFormatter(
                DEFAULT_LOG_FORMAT,
                datefmt=DEFAULT_DATE_FORMAT,
                log_colors=LOG_COLORS
            )
        )
        self.logger.addHandler(handler)

def setup_logger(
    name: str = "test-radar",
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True
) -> logging.Logger:
    """Setup and return a configured logger
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        console: Whether to enable console output
        
    Returns:
        Configured logger instance
    """
    logger = RadarLogger(
        name=name,
        level=level,
        log_file=log_file,
        console=console
    )
    return logger.logger

# Default logger instance
logger = setup_logger()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance
    
    Args:
        name: Optional logger name
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)
    return logger