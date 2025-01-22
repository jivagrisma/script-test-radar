"""
Custom exceptions for test-radar.
Provides specific exception types for different error scenarios.
"""

from typing import Any, Dict, Optional

class RadarError(Exception):
    """Base exception class for test-radar"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """Initialize exception
        
        Args:
            message: Error message
            details: Optional error details
            cause: Optional causing exception
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """String representation including details"""
        result = self.message
        if self.details:
            result += f"\nDetails: {self.details}"
        if self.cause:
            result += f"\nCaused by: {str(self.cause)}"
        return result

class ConfigError(RadarError):
    """Configuration related errors"""
    pass

class ExecutionError(RadarError):
    """Test execution related errors"""
    pass

class ScannerError(RadarError):
    """Test discovery/scanning related errors"""
    pass

class ParserError(RadarError):
    """Test parsing related errors"""
    pass

class CoverageError(RadarError):
    """Coverage analysis related errors"""
    pass

class VSCodeError(RadarError):
    """VSCode integration related errors"""
    pass

class LLMError(RadarError):
    """LLM integration related errors"""
    pass

class ValidationError(RadarError):
    """Data validation related errors"""
    pass

class CacheError(RadarError):
    """Cache related errors"""
    pass

class ResourceError(RadarError):
    """Resource management related errors"""
    pass

class ReportError(RadarError):
    """Report generation related errors"""
    pass

def wrap_exception(
    exc: Exception,
    message: str,
    error_type: type = RadarError,
    details: Optional[Dict[str, Any]] = None
) -> RadarError:
    """Wrap an exception with additional context
    
    Args:
        exc: Original exception
        message: New error message
        error_type: Type of error to create
        details: Optional error details
        
    Returns:
        Wrapped exception
    """
    return error_type(message, details=details, cause=exc)