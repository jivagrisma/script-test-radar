"""
Test reporter implementation.
Provides functionality for generating test reports and coverage analysis.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from ..core.config import TestConfig
from ..core.exceptions import ReportError
from ..core.logger import get_logger
from ..executor.executor import TestResult
from ..scanner.scanner import TestInfo

logger = get_logger(__name__)

class TestReport:
    """Container for test execution report data"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.total_duration = 0.0
        self.total_coverage = 0.0
        self.results: Dict[str, TestResult] = {}
        self.timestamp = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Calculate test success rate"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def average_duration(self) -> float:
        """Calculate average test duration"""
        if self.total_tests == 0:
            return 0.0
        return self.total_duration / self.total_tests

class TestReporter:
    """Reporter for generating test execution reports"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.console = Console()
    
    def generate_report(
        self,
        tests: List[TestInfo],
        results: Dict[str, TestResult]
    ) -> TestReport:
        """Generate test execution report
        
        Args:
            tests: List of executed tests
            results: Dictionary mapping test IDs to results
            
        Returns:
            Generated report
        """
        report = TestReport()
        report.total_tests = len(tests)
        
        for test in tests:
            result = results.get(test.id)
            if not result:
                continue
                
            report.results[test.id] = result
            report.total_duration += result.duration
            
            if result.coverage is not None:
                report.total_coverage += result.coverage
            
            if result.status == "passed":
                report.passed_tests += 1
            elif result.status == "failed":
                report.failed_tests += 1
            elif result.status == "error":
                report.error_tests += 1
            elif result.status == "skipped":
                report.skipped_tests += 1
        
        # Calculate average coverage
        if report.total_tests > 0:
            report.total_coverage /= report.total_tests
        
        return report
    
    def print_report(self, report: TestReport) -> None:
        """Print test report to console
        
        Args:
            report: Test report to print
        """
        # Summary table
        summary = Table(title="Test Execution Summary")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green")
        
        summary.add_row("Total Tests", str(report.total_tests))
        summary.add_row("Passed", f"[green]{report.passed_tests}[/green]")
        summary.add_row("Failed", f"[red]{report.failed_tests}[/red]")
        summary.add_row("Errors", f"[red]{report.error_tests}[/red]")
        summary.add_row("Skipped", f"[yellow]{report.skipped_tests}[/yellow]")
        summary.add_row("Success Rate", f"{report.success_rate:.2f}%")
        summary.add_row("Total Duration", f"{report.total_duration:.2f}s")
        summary.add_row("Average Duration", f"{report.average_duration:.2f}s")
        summary.add_row("Average Coverage", f"{report.total_coverage:.2f}%")
        
        self.console.print(summary)
        
        # Results table
        if report.results:
            results_table = Table(title="Test Results")
            results_table.add_column("Test", style="cyan")
            results_table.add_column("Status", style="green")
            results_table.add_column("Duration", style="blue")
            results_table.add_column("Coverage", style="magenta")
            
            for test_id, result in report.results.items():
                status_style = {
                    "passed": "[green]PASS[/green]",
                    "failed": "[red]FAIL[/red]",
                    "error": "[red]ERROR[/red]",
                    "skipped": "[yellow]SKIP[/yellow]"
                }.get(result.status, result.status)
                
                coverage = f"{result.coverage:.2f}%" if result.coverage is not None else "N/A"
                
                results_table.add_row(
                    test_id,
                    status_style,
                    f"{result.duration:.2f}s",
                    coverage
                )
            
            self.console.print(results_table)
    
    def save_report(self, report: TestReport, output_path: Path) -> None:
        """Save test report to file
        
        Args:
            report: Test report to save
            output_path: Path to save report to
            
        Raises:
            ReportError: If report cannot be saved
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with output_path.open('w') as f:
                # Write summary
                f.write("Test Execution Summary\n")
                f.write("=====================\n\n")
                f.write(f"Timestamp: {report.timestamp}\n")
                f.write(f"Total Tests: {report.total_tests}\n")
                f.write(f"Passed: {report.passed_tests}\n")
                f.write(f"Failed: {report.failed_tests}\n")
                f.write(f"Errors: {report.error_tests}\n")
                f.write(f"Skipped: {report.skipped_tests}\n")
                f.write(f"Success Rate: {report.success_rate:.2f}%\n")
                f.write(f"Total Duration: {report.total_duration:.2f}s\n")
                f.write(f"Average Duration: {report.average_duration:.2f}s\n")
                f.write(f"Average Coverage: {report.total_coverage:.2f}%\n\n")
                
                # Write detailed results
                f.write("Detailed Results\n")
                f.write("===============\n\n")
                
                for test_id, result in report.results.items():
                    f.write(f"Test: {test_id}\n")
                    f.write(f"Status: {result.status}\n")
                    f.write(f"Duration: {result.duration:.2f}s\n")
                    
                    if result.coverage is not None:
                        f.write(f"Coverage: {result.coverage:.2f}%\n")
                    else:
                        f.write("Coverage: N/A\n")
                    
                    if result.message:
                        f.write(f"Message: {result.message}\n")
                    if result.traceback:
                        f.write(f"Traceback:\n{result.traceback}\n")
                    if result.stdout:
                        f.write(f"Stdout:\n{result.stdout}\n")
                    if result.stderr:
                        f.write(f"Stderr:\n{result.stderr}\n")
                    
                    f.write("\n")
                    
        except Exception as e:
            raise ReportError(f"Failed to save report to {output_path}", cause=e)