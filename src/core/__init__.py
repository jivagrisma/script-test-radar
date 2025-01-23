"""
Core functionality for test-radar.
This module contains the central components and interfaces.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Version info
__version__ = "0.1.0"
__author__ = "Roo"

# Type aliases
PathLike = Union[str, Path]
JsonDict = Dict[str, Any]

# Core components
from .config import AWSConfig, LLMConfig, RadarConfig, TestConfig, VSCodeConfig
from .exceptions import (
    AnalysisError,
    APIError,
    AuthenticationError,
    BedRockError,
    ConfigError,
    CoverageError,
    DependencyError,
    ExecutionError,
    FileSystemError,
    LLMError,
    ParallelExecutionError,
    RadarError,
    RateLimitError,
    ReportError,
    ResourceError,
    ScanError,
    ScannerError,
    TimeoutError,
    ValidationError,
)
from .logger import get_logger, setup_logger

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Type aliases
    "PathLike",
    "JsonDict",
    # Config
    "RadarConfig",
    "TestConfig",
    "VSCodeConfig",
    "LLMConfig",
    "AWSConfig",
    # Logger
    "setup_logger",
    "get_logger",
    # Exceptions
    "RadarError",
    "ConfigError",
    "ScanError",
    "ScannerError",
    "ExecutionError",
    "ReportError",
    "LLMError",
    "BedRockError",
    "ValidationError",
    "TimeoutError",
    "ResourceError",
    "ParallelExecutionError",
    "CoverageError",
    "AnalysisError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "DependencyError",
    "FileSystemError",
]
