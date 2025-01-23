"""
Logging configuration for test-radar.

Provides centralized logging setup and utilities.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.logging import RichHandler

# Constants
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Rich console for fancy output
console = Console()


class RadarLogger:
    """Custom logger with rich output and file logging."""

    def __init__(
        self,
        name: str,
        level: str = DEFAULT_LOG_LEVEL,
        log_file: Optional[str] = None,
        format: str = DEFAULT_LOG_FORMAT,
    ) -> None:
        """Initialize logger.

        Args:
            name: Logger name.
            level: Log level.
            log_file: Optional log file path.
            format: Log format string.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.upper())

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add rich console handler
        rich_handler = RichHandler(
            console=console, show_path=False, enable_link_path=True
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(rich_handler)

        # Add file handler if log file specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(format))
            self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log info message.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log error message.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        """Log exception with traceback.

        Args:
            msg: Message to log.
            *args: Additional positional arguments.
            exc_info: Whether to include exception info.
            **kwargs: Additional keyword arguments.
        """
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)


class TestLogger(RadarLogger):
    """Logger specifically for test execution."""

    def __init__(self, test_id: str, **kwargs: Any) -> None:
        """Initialize test logger.

        Args:
            test_id: Test identifier.
            **kwargs: Additional logger arguments.
        """
        super().__init__(f"test.{test_id}", **kwargs)
        self.test_id = test_id

    def start_test(self) -> None:
        """Log test start."""
        self.info(f"Starting test {self.test_id}")

    def end_test(self, status: str, duration: float) -> None:
        """Log test completion.

        Args:
            status: Test status.
            duration: Test duration in seconds.
        """
        self.info(f"Test {self.test_id} {status} (duration: {duration:.2f}s)")

    def log_error(self, error: Exception, traceback: Optional[str] = None) -> None:
        """Log test error.

        Args:
            error: Exception that occurred.
            traceback: Optional traceback string.
        """
        self.error(f"Test {self.test_id} failed: {str(error)}")
        if traceback:
            self.debug(f"Traceback:\n{traceback}")


class AnalysisLogger(RadarLogger):
    """Logger specifically for test analysis."""

    def __init__(self, test_id: str, **kwargs: Any) -> None:
        """Initialize analysis logger.

        Args:
            test_id: Test identifier.
            **kwargs: Additional logger arguments.
        """
        super().__init__(f"analysis.{test_id}", **kwargs)
        self.test_id = test_id

    def log_analysis_start(self) -> None:
        """Log analysis start."""
        self.info(f"Starting analysis of test {self.test_id}")

    def log_analysis_result(self, issues: int, suggestions: int, fixes: int) -> None:
        """Log analysis results.

        Args:
            issues: Number of issues found.
            suggestions: Number of suggestions made.
            fixes: Number of fixes proposed.
        """
        self.info(
            f"Analysis complete for {self.test_id}: "
            f"{issues} issues, {suggestions} suggestions, "
            f"{fixes} fixes"
        )

    def log_llm_error(self, error: Exception) -> None:
        """Log LLM-related error.

        Args:
            error: Exception that occurred.
        """
        self.error(f"LLM analysis failed for {self.test_id}: {str(error)}")


def setup_logger(level: Optional[str] = None, log_file: Optional[str] = None) -> RadarLogger:
    """Set up root logger.

    Args:
        level: Optional log level override.
        log_file: Optional log file path.

    Returns:
        Configured logger.
    """
    # Get log level from environment or use default
    log_level = (level or os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)).upper()

    # Get log file from environment if not provided
    log_file = log_file or os.getenv("LOG_FILE")

    # Create logger
    logger = RadarLogger("test_radar", level=log_level, log_file=log_file)

    # Log startup information
    logger.info("Test Radar starting up")
    logger.info(f"Log level: {log_level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")

    return logger


def get_logger(name: str) -> RadarLogger:
    """Get logger for module.

    Args:
        name: Module name.

    Returns:
        Logger instance.
    """
    return RadarLogger(name)


# Configure logging on import
logger = setup_logger()
