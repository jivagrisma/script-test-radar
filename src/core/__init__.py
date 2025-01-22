"""
Core functionality for test-radar.
This module contains the central components and interfaces.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Version info
__version__ = "0.1.0"
__author__ = "Roo"

# Type aliases
PathLike = Union[str, Path]
JsonDict = Dict[str, Any]

# Core components
from .config import RadarConfig, TestConfig, VSCodeConfig, LLMConfig, AWSConfig
from .logger import setup_logger, get_logger
from .exceptions import (
    RadarError,
    ConfigError,
    ExecutionError,
    ScannerError,
    ParserError,
    CoverageError,
    VSCodeError,
    LLMError,
    ValidationError,
    CacheError,
    ResourceError,
    ReportError,
    wrap_exception
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Type aliases
    'PathLike',
    'JsonDict',
    
    # Config
    'RadarConfig',
    'TestConfig',
    'VSCodeConfig',
    'LLMConfig',
    'AWSConfig',
    
    # Logger
    'setup_logger',
    'get_logger',
    
    # Exceptions
    'RadarError',
    'ConfigError',
    'ExecutionError',
    'ScannerError',
    'ParserError',
    'CoverageError',
    'VSCodeError',
    'LLMError',
    'ValidationError',
    'CacheError',
    'ResourceError',
    'ReportError',
    'wrap_exception'
]