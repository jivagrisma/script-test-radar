"""
Custom exceptions for test-radar.

Provides specific exception types for different error scenarios.
"""

from typing import Any, List, Optional


class RadarError(Exception):
    """Base exception for all test-radar errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """Initialize RadarError.

        Args:
            message: Error message.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.cause = cause
        self.message = message

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional cause.
        """
        if self.cause:
            return f"{self.message} (Caused by: {str(self.cause)})"
        return self.message


class ConfigError(RadarError):
    """Error in configuration loading or validation."""

    pass


class ScanError(RadarError):
    """Error during test scanning."""

    pass


class ScannerError(RadarError):
    """Error in scanner operations."""

    pass


class ExecutionError(RadarError):
    """Error during test execution."""

    pass


class ReportError(RadarError):
    """Error during report generation."""

    pass


class LLMError(RadarError):
    """Error in LLM operations."""

    pass


class BedRockError(LLMError):
    """Specific error for AWS Bedrock operations."""

    def __init__(self, message: str, cause: Optional[Exception] = None, model_id: Optional[str] = None) -> None:
        """Initialize BedRockError.

        Args:
            message: Error message.
            cause: Optional underlying exception.
            model_id: Optional Bedrock model identifier.
        """
        super().__init__(message, cause)
        self.model_id = model_id

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional model ID.
        """
        base = super().__str__()
        if self.model_id:
            return f"{base} (Model: {self.model_id})"
        return base


class ValidationError(RadarError):
    """Error in data validation."""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None) -> None:
        """Initialize ValidationError.

        Args:
            message: Error message.
            field: Optional field name that failed validation.
            value: Optional invalid value.
        """
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional field and value details.
        """
        if self.field and self.value:
            return f"{self.message} (Field: {self.field}, Value: {self.value})"
        return self.message


class TimeoutError(ExecutionError):
    """Error when operation times out."""

    def __init__(self, message: str, timeout: Optional[float] = None) -> None:
        """Initialize TimeoutError.

        Args:
            message: Error message.
            timeout: Optional timeout duration in seconds.
        """
        super().__init__(message)
        self.timeout = timeout

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional timeout duration.
        """
        if self.timeout:
            return f"{self.message} (Timeout: {self.timeout}s)"
        return self.message


class ResourceError(RadarError):
    """Error accessing resources."""

    def __init__(self, message: str, resource: Optional[str] = None) -> None:
        """Initialize ResourceError.

        Args:
            message: Error message.
            resource: Optional resource identifier.
        """
        super().__init__(message)
        self.resource = resource

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional resource details.
        """
        if self.resource:
            return f"{self.message} (Resource: {self.resource})"
        return self.message


class ParallelExecutionError(ExecutionError):
    """Error in parallel test execution."""

    def __init__(self, message: str, failed_tests: Optional[List[str]] = None) -> None:
        """Initialize ParallelExecutionError.

        Args:
            message: Error message.
            failed_tests: Optional list of failed test identifiers.
        """
        super().__init__(message)
        self.failed_tests = failed_tests or []

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional list of failed tests.
        """
        base = super().__str__()
        if self.failed_tests:
            return f"{base} (Failed tests: {', '.join(self.failed_tests)})"
        return base


class CoverageError(ExecutionError):
    """Error in coverage calculation."""

    def __init__(self, message: str, coverage: Optional[float] = None, target: Optional[float] = None) -> None:
        """Initialize CoverageError.

        Args:
            message: Error message.
            coverage: Optional actual coverage percentage.
            target: Optional target coverage percentage.
        """
        super().__init__(message)
        self.coverage = coverage
        self.target = target

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional coverage details.
        """
        if self.coverage is not None and self.target is not None:
            return f"{self.message} (Coverage: {self.coverage}%, Target: {self.target}%)"
        return self.message


class AnalysisError(LLMError):
    """Error during test analysis."""

    def __init__(self, message: str, test_id: Optional[str] = None) -> None:
        """Initialize AnalysisError.

        Args:
            message: Error message.
            test_id: Optional test identifier.
        """
        super().__init__(message)
        self.test_id = test_id

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional test identifier.
        """
        if self.test_id:
            return f"{self.message} (Test: {self.test_id})"
        return self.message


class APIError(RadarError):
    """Error in API operations."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None) -> None:
        """Initialize APIError.

        Args:
            message: Error message.
            status_code: Optional HTTP status code.
            response: Optional API response text.
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional status code and response.
        """
        base = super().__str__()
        if self.status_code:
            return f"{base} (Status: {self.status_code}, Response: {self.response})"
        return base


class AuthenticationError(APIError):
    """Error in authentication."""

    pass


class RateLimitError(APIError):
    """Error when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        """Initialize RateLimitError.

        Args:
            message: Error message.
            retry_after: Optional number of seconds to wait before retrying.
        """
        super().__init__(message)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional retry delay.
        """
        if self.retry_after:
            return f"{self.message} (Retry after: {self.retry_after}s)"
        return self.message


class DependencyError(RadarError):
    """Error in managing dependencies."""

    def __init__(self, message: str, dependency: Optional[str] = None) -> None:
        """Initialize DependencyError.

        Args:
            message: Error message.
            dependency: Optional dependency name.
        """
        super().__init__(message)
        self.dependency = dependency

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional dependency details.
        """
        if self.dependency:
            return f"{self.message} (Dependency: {self.dependency})"
        return self.message


class FileSystemError(ResourceError):
    """Error in file system operations."""

    def __init__(self, message: str, path: Optional[str] = None, operation: Optional[str] = None) -> None:
        """Initialize FileSystemError.

        Args:
            message: Error message.
            path: Optional file system path.
            operation: Optional operation type.
        """
        super().__init__(message)
        self.path = path
        self.operation = operation

    def __str__(self) -> str:
        """Get string representation of the error.

        Returns:
            Error message with optional path and operation details.
        """
        base = super().__str__()
        if self.path and self.operation:
            return f"{base} (Operation: {self.operation}, Path: {self.path})"
        return base
