"""
Test executor implementation.

Handles parallel test execution and result collection.
"""

import asyncio
import concurrent.futures
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..core.config import TestConfig
from ..core.exceptions import ExecutionError
from ..core.logger import get_logger
from ..scanner.scanner import TestInfo

logger = get_logger(__name__)


@dataclass
class TestResult:
    """Result of a test execution."""

    test_id: str
    status: str  # "passed", "failed", "error", "skipped"
    duration: float
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    coverage: Optional[float] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None


class TestExecutor:
    """Executor for running tests in parallel."""

    def __init__(self, config: TestConfig) -> None:
        """Initialize executor with configuration.

        Args:
            config: Test configuration.
        """
        self.config = config
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.parallel_jobs or None
        )

    async def run_test(self, test: TestInfo) -> TestResult:
        """Run a single test.

        Args:
            test: Test to run.

        Returns:
            Test execution result.

        Raises:
            ExecutionError: If test execution fails.
        """
        start_time = time.time()

        try:
            # Prepare pytest command
            cmd = [
                self.config.python_path,
                "-m",
                "pytest",
                str(test.file_path),
                "-v",
                "--tb=short",
                f"--timeout={self.config.timeout}",
                "--capture=tee-sys",
            ]

            # Add coverage if enabled
            if self.config.coverage_target > 0:
                cmd.extend(
                    [
                        "--cov",
                        "--cov-report=term-missing",
                    ]
                )

            # Add test selection
            if test.class_name:
                cmd.append(f"{test.class_name}::{test.function_name}")
            else:
                cmd.append(f"{test.function_name}")

            # Run test in subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return TestResult(
                    test_id=test.id,
                    status="error",
                    duration=time.time() - start_time,
                    error_message="Test execution timed out",
                    error_type="TimeoutError",
                )

            # Parse output
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")

            # Extract coverage
            coverage: Optional[float] = None
            for line in stdout.splitlines():
                if "TOTAL" in line and "%" in line:
                    try:
                        coverage = float(line.split("%")[0].strip().split()[-1])
                    except (ValueError, IndexError):
                        pass

            # Determine status
            if process.returncode == 0:
                status = "passed"
            elif process.returncode == 1:
                status = "failed"
            elif process.returncode == 5:
                status = "skipped"
            else:
                status = "error"

            # Extract error information
            error_message: Optional[str] = None
            error_type: Optional[str] = None
            error_traceback: Optional[str] = None

            if status in ("failed", "error"):
                # Parse pytest output for error information
                error_lines: List[str] = []
                in_traceback = False

                for line in stderr.splitlines():
                    if line.startswith("E   "):
                        if not error_message:
                            error_message = line[4:]
                        error_lines.append(line[4:])
                    elif "Traceback" in line:
                        in_traceback = True
                    elif in_traceback and line.strip():
                        error_lines.append(line)

                if error_lines:
                    error_traceback = "\n".join(error_lines)
                    # Try to extract error type
                    for line in error_lines:
                        if ": " in line:
                            error_type = line.split(": ")[0].strip()
                            break

            return TestResult(
                test_id=test.id,
                status=status,
                duration=time.time() - start_time,
                stdout=stdout,
                stderr=stderr,
                coverage=coverage,
                error_message=error_message,
                error_type=error_type,
                error_traceback=error_traceback,
            )

        except Exception as e:
            return TestResult(
                test_id=test.id,
                status="error",
                duration=time.time() - start_time,
                error_message=str(e),
                error_type=type(e).__name__,
            )

    async def run_tests(self, tests: List[TestInfo]) -> Dict[str, TestResult]:
        """Run multiple tests in parallel.

        Args:
            tests: Tests to run.

        Returns:
            Dictionary mapping test IDs to results.

        Raises:
            ExecutionError: If test execution fails.
        """
        try:
            # Create tasks for each test
            tasks: List[Tuple[str, asyncio.Task[TestResult]]] = []
            for test in tests:
                task = asyncio.create_task(self.run_test(test))
                tasks.append((test.id, task))

            # Wait for all tasks to complete
            results: Dict[str, TestResult] = {}
            for test_id, task in tasks:
                try:
                    result = await task
                    results[test_id] = result
                except Exception as e:
                    logger.error(f"Failed to run test {test_id}: {e}")
                    results[test_id] = TestResult(
                        test_id=test_id,
                        status="error",
                        duration=0.0,
                        error_message=str(e),
                        error_type=type(e).__name__,
                    )

            return results

        except Exception as e:
            raise ExecutionError(f"Failed to run tests: {str(e)}")

    def get_coverage_report(self, results: Dict[str, TestResult]) -> Dict[str, float]:
        """Generate coverage report from test results.

        Args:
            results: Test results.

        Returns:
            Dictionary mapping files to coverage percentages.
        """
        coverage: Dict[str, float] = {}

        for result in results.values():
            if result.coverage is not None and result.stdout:
                # Parse coverage output to get per-file coverage
                for line in result.stdout.splitlines():
                    if ".py" in line and "%" in line:
                        try:
                            parts = line.strip().split()
                            file_path = parts[0]
                            percentage = float(parts[-1].rstrip("%"))
                            coverage[file_path] = percentage
                        except (ValueError, IndexError):
                            continue

        return coverage
