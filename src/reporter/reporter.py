"""
Test reporter implementation.
Generates detailed reports from test results and analysis.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from ..analyzer.llm_analyzer import TestAnalysis
from ..core.config import TestConfig
from ..core.exceptions import ReportError
from ..core.logger import get_logger
from ..executor.executor import TestResult
from ..scanner.scanner import TestInfo

logger = get_logger(__name__)


@dataclass
class TestReport:
    """Complete test execution and analysis report"""

    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    skipped_tests: int
    total_duration: float
    average_duration: float
    coverage: Optional[float] = None
    test_results: Dict[str, TestResult] = None
    analyses: Dict[str, TestAnalysis] = None


class TestReporter:
    """Reporter for generating test reports"""

    def __init__(self, config: TestConfig):
        """Initialize reporter with configuration

        Args:
            config: Test configuration
        """
        self.config = config
        self.console = Console()

    def generate_report(
        self,
        tests: List[TestInfo],
        results: Dict[str, TestResult],
        analyses: Optional[Dict[str, TestAnalysis]] = None,
    ) -> TestReport:
        """Generate complete test report

        Args:
            tests: List of tests
            results: Test execution results
            analyses: Optional test analyses

        Returns:
            Complete test report
        """
        # Calculate statistics
        total_tests = len(tests)
        passed_tests = sum(1 for r in results.values() if r.status == "passed")
        failed_tests = sum(1 for r in results.values() if r.status == "failed")
        error_tests = sum(1 for r in results.values() if r.status == "error")
        skipped_tests = sum(1 for r in results.values() if r.status == "skipped")

        # Calculate durations
        total_duration = sum(r.duration for r in results.values())
        average_duration = total_duration / total_tests if total_tests > 0 else 0

        # Calculate overall coverage
        coverage = None
        coverage_values = [
            r.coverage for r in results.values() if r.coverage is not None
        ]
        if coverage_values:
            coverage = sum(coverage_values) / len(coverage_values)

        return TestReport(
            timestamp=datetime.now().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            error_tests=error_tests,
            skipped_tests=skipped_tests,
            total_duration=total_duration,
            average_duration=average_duration,
            coverage=coverage,
            test_results=results,
            analyses=analyses,
        )

    def print_report(self, report: TestReport):
        """Print report to console

        Args:
            report: Test report to print
        """
        # Print summary
        self.console.print("\n[bold cyan]Test Execution Summary[/bold cyan]")

        summary_table = Table(show_header=True)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Tests", str(report.total_tests))
        summary_table.add_row("Passed", f"[green]{report.passed_tests}[/green]")
        summary_table.add_row("Failed", f"[red]{report.failed_tests}[/red]")
        summary_table.add_row("Errors", f"[red]{report.error_tests}[/red]")
        summary_table.add_row("Skipped", f"[yellow]{report.skipped_tests}[/yellow]")
        summary_table.add_row("Total Duration", f"{report.total_duration:.2f}s")
        summary_table.add_row("Average Duration", f"{report.average_duration:.2f}s")
        if report.coverage is not None:
            summary_table.add_row("Coverage", f"{report.coverage:.1f}%")

        self.console.print(summary_table)

        # Print test results
        self.console.print("\n[bold cyan]Test Results[/bold cyan]")

        results_table = Table(show_header=True)
        results_table.add_column("Test ID", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Duration", style="blue")
        results_table.add_column("Coverage", style="magenta")

        for test_id, result in report.test_results.items():
            status_style = {
                "passed": "[green]PASS[/green]",
                "failed": "[red]FAIL[/red]",
                "error": "[red]ERROR[/red]",
                "skipped": "[yellow]SKIP[/yellow]",
            }.get(result.status, result.status)

            results_table.add_row(
                test_id,
                status_style,
                f"{result.duration:.2f}s",
                f"{result.coverage:.1f}%" if result.coverage else "N/A",
            )

        self.console.print(results_table)

        # Print analyses if available
        if report.analyses:
            self.console.print("\n[bold cyan]Test Analyses[/bold cyan]")

            for test_id, analysis in report.analyses.items():
                self.console.print(f"\n[bold]{test_id}[/bold]")

                if analysis.issues:
                    self.console.print("\n[red]Issues:[/red]")
                    for issue in analysis.issues:
                        self.console.print(f"  • {issue}")

                if analysis.suggestions:
                    self.console.print("\n[green]Suggestions:[/green]")
                    for suggestion in analysis.suggestions:
                        self.console.print(f"  • {suggestion}")

                if analysis.coverage_gaps:
                    self.console.print("\n[yellow]Coverage Gaps:[/yellow]")
                    for gap in analysis.coverage_gaps:
                        self.console.print(f"  • {gap}")

    def save_report(self, report: TestReport, output_path: Path):
        """Save report to file

        Args:
            report: Test report to save
            output_path: Path to save report to

        Raises:
            ReportError: If report cannot be saved
        """
        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert report to JSON
            report_dict = {
                "timestamp": report.timestamp,
                "summary": {
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "failed_tests": report.failed_tests,
                    "error_tests": report.error_tests,
                    "skipped_tests": report.skipped_tests,
                    "total_duration": report.total_duration,
                    "average_duration": report.average_duration,
                    "coverage": report.coverage,
                },
                "results": {
                    test_id: asdict(result)
                    for test_id, result in report.test_results.items()
                },
                "analyses": {
                    test_id: asdict(analysis)
                    for test_id, analysis in (report.analyses or {}).items()
                },
            }

            # Save as JSON
            if output_path.suffix == ".json":
                with open(output_path, "w") as f:
                    json.dump(report_dict, f, indent=2)

            # Save as HTML
            elif output_path.suffix == ".html":
                html = self._generate_html_report(report_dict)
                with open(output_path, "w") as f:
                    f.write(html)

            # Save as text
            else:
                with open(output_path, "w") as f:
                    self._write_text_report(report_dict, f)

        except Exception as e:
            raise ReportError(f"Failed to save report: {str(e)}")

    def _generate_html_report(self, report_dict: dict) -> str:
        """Generate HTML report

        Args:
            report_dict: Report data

        Returns:
            HTML report content
        """
        # Generate test results table rows
        test_rows = []
        for test_id, result in report_dict["results"].items():
            coverage_text = (
                f"{result['coverage']:.1f}%" if result.get("coverage") else "N/A"
            )
            test_rows.append(
                f"""
            <tr>
                <td>{test_id}</td>
                <td class="{result['status']}">{result['status'].upper()}</td>
                <td>{result['duration']:.2f}s</td>
                <td>{coverage_text}</td>
            </tr>
            """
            )

        # Generate analysis sections
        analysis_sections = []
        for test_id, analysis in report_dict.get("analyses", {}).items():
            issues_list = "".join(
                f"<li>{issue}</li>" for issue in analysis.get("issues", [])
            )
            suggestions_list = "".join(
                f"<li>{suggestion}</li>"
                for suggestion in analysis.get("suggestions", [])
            )
            gaps_list = "".join(
                f"<li>{gap}</li>" for gap in analysis.get("coverage_gaps", [])
            )

            analysis_sections.append(
                f"""
            <div class="analysis">
                <h2>Analysis: {test_id}</h2>

                <h3>Issues</h3>
                <ul>{issues_list}</ul>

                <h3>Suggestions</h3>
                <ul>{suggestions_list}</ul>

                <h3>Coverage Gaps</h3>
                <ul>{gaps_list}</ul>
            </div>
            """
            )

        # Simple HTML template
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; }}
                h1, h2 {{ color: #333; }}
                .summary {{ margin: 1em 0; }}
                .results {{ margin: 1em 0; }}
                .analysis {{ margin: 1em 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ padding: 0.5em; text-align: left; border: 1px solid #ddd; }}
                th {{ background: #f5f5f5; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .skip {{ color: orange; }}
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <p>Generated: {report_dict['timestamp']}</p>

            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr><th>Total Tests</th><td>{report_dict['summary']['total_tests']}</td></tr>
                    <tr><th>Passed</th><td class="pass">{report_dict['summary']['passed_tests']}</td></tr>
                    <tr><th>Failed</th><td class="fail">{report_dict['summary']['failed_tests']}</td></tr>
                    <tr><th>Errors</th><td class="fail">{report_dict['summary']['error_tests']}</td></tr>
                    <tr><th>Skipped</th><td class="skip">{report_dict['summary']['skipped_tests']}</td></tr>
                    <tr><th>Total Duration</th><td>{report_dict['summary']['total_duration']:.2f}s</td></tr>
                    <tr><th>Average Duration</th><td>{report_dict['summary']['average_duration']:.2f}s</td></tr>
                    <tr><th>Coverage</th><td>{report_dict['summary']['coverage']:.1f}%</td></tr>
                </table>
            </div>

            <div class="results">
                <h2>Test Results</h2>
                <table>
                    <tr>
                        <th>Test ID</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Coverage</th>
                    </tr>
                    {''.join(test_rows)}
                </table>
            </div>

            {''.join(analysis_sections)}
        </body>
        </html>
        """

    def _write_text_report(self, report_dict: dict, file):
        """Write text report

        Args:
            report_dict: Report data
            file: File to write to
        """
        # Write summary
        file.write("Test Report\n")
        file.write("===========\n\n")
        file.write(f"Generated: {report_dict['timestamp']}\n\n")

        file.write("Summary\n")
        file.write("-------\n")
        for key, value in report_dict["summary"].items():
            if isinstance(value, float):
                file.write(f"{key}: {value:.2f}\n")
            else:
                file.write(f"{key}: {value}\n")

        # Write results
        file.write("\nTest Results\n")
        file.write("------------\n")
        for test_id, result in report_dict["results"].items():
            file.write(f"\n{test_id}:\n")
            for key, value in result.items():
                if isinstance(value, float):
                    file.write(f"  {key}: {value:.2f}\n")
                else:
                    file.write(f"  {key}: {value}\n")

        # Write analyses
        if report_dict.get("analyses"):
            file.write("\nTest Analyses\n")
            file.write("-------------\n")
            for test_id, analysis in report_dict["analyses"].items():
                file.write(f"\n{test_id}:\n")

                if analysis.get("issues"):
                    file.write("\nIssues:\n")
                    for issue in analysis["issues"]:
                        file.write(f"  • {issue}\n")

                if analysis.get("suggestions"):
                    file.write("\nSuggestions:\n")
                    for suggestion in analysis["suggestions"]:
                        file.write(f"  • {suggestion}\n")

                if analysis.get("coverage_gaps"):
                    file.write("\nCoverage Gaps:\n")
                    for gap in analysis["coverage_gaps"]:
                        file.write(f"  • {gap}\n")
