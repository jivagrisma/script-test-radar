"""
Test executor implementation.
Provides functionality for running tests and collecting results.
"""

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..core.config import TestConfig
from ..core.exceptions import ExecutionError
from ..core.logger import get_logger
from ..scanner.scanner import TestInfo

logger = get_logger(__name__)

@dataclass
class TestResult:
    """Result of a test execution"""
    test_id: str
    status: str  # 'passed', 'failed', 'error', 'skipped'
    duration: float
    message: Optional[str] = None
    traceback: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    coverage: Optional[float] = None
    timestamp: datetime = datetime.now()

class TestExecutor:
    """Executor for running tests"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self._running: Set[str] = set()
        self._results: Dict[str, TestResult] = {}
    
    async def _run_test(self, test: TestInfo) -> TestResult:
        """Run a single test
        
        Args:
            test: Test to run
            
        Returns:
            Test execution result
        """
        if test.id in self._running:
            raise ExecutionError(f"Test {test.id} is already running")
        
        self._running.add(test.id)
        start_time = datetime.now()
        
        try:
            cmd = [
                self.config.python_path,
                "-m", "pytest",
                str(test.file_path),
                "-v",
                "--tb=short",
                f"--timeout={self.config.timeout}",
                "--cov",
                f"-k={test.name}"
            ]
            
            if test.class_name:
                cmd.append(f"{test.class_name}::{test.name}")
            else:
                cmd.append(test.name)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            duration = (datetime.now() - start_time).total_seconds()
            
            stdout_str = stdout.decode() if stdout else None
            stderr_str = stderr.decode() if stderr else None
            
            # Parse pytest output
            if process.returncode == 0:
                status = "passed"
                message = None
            elif process.returncode == 1:
                status = "failed"
                message = self._extract_failure_message(stdout_str or "")
            elif process.returncode == 2:
                status = "error"
                message = stderr_str
            else:
                status = "error"
                message = f"Process returned {process.returncode}"
            
            # Extract coverage if available
            coverage = self._extract_coverage(stdout_str or "")
            
            result = TestResult(
                test_id=test.id,
                status=status,
                duration=duration,
                message=message,
                stdout=stdout_str,
                stderr=stderr_str,
                coverage=coverage
            )
            
            self._results[test.id] = result
            return result
            
        except asyncio.TimeoutError:
            return TestResult(
                test_id=test.id,
                status="error",
                duration=self.config.timeout,
                message=f"Test timed out after {self.config.timeout} seconds"
            )
            
        except Exception as e:
            return TestResult(
                test_id=test.id,
                status="error",
                duration=0.0,
                message=str(e)
            )
            
        finally:
            self._running.remove(test.id)
    
    def _extract_failure_message(self, output: str) -> Optional[str]:
        """Extract failure message from pytest output"""
        # TODO: Implement proper pytest output parsing
        return output.split("FAILED")[-1].strip() if "FAILED" in output else None
    
    def _extract_coverage(self, output: str) -> Optional[float]:
        """Extract coverage percentage from pytest-cov output"""
        try:
            # Look for coverage percentage in output
            for line in output.split('\n'):
                if "TOTAL" in line and "%" in line:
                    return float(line.split()[-1].strip('%'))
        except:
            pass
        return None
    
    async def run_tests(self, tests: List[TestInfo]) -> Dict[str, TestResult]:
        """Run multiple tests in parallel
        
        Args:
            tests: List of tests to run
            
        Returns:
            Dictionary mapping test IDs to results
        """
        jobs = self.config.parallel_jobs or len(tests)
        tasks = [self._run_test(test) for test in tests]
        
        results = await asyncio.gather(*tasks)
        return {result.test_id: result for result in results}
    
    def get_result(self, test_id: str) -> Optional[TestResult]:
        """Get result for a specific test
        
        Args:
            test_id: Test identifier
            
        Returns:
            Test result if available
        """
        return self._results.get(test_id)
    
    def clear_results(self) -> None:
        """Clear all test results"""
        self._results.clear()
    
    @property
    def is_running(self) -> bool:
        """Check if any tests are currently running"""
        return bool(self._running)