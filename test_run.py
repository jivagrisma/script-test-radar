#!/usr/bin/env python3
"""
Main entry point for test-radar.
Provides command line interface for running tests and analysis.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console

from src.analyzer.llm_analyzer import LLMAnalyzer
from src.core.config import RadarConfig, load_config
from src.core.exceptions import RadarError
from src.core.logger import setup_logger
from src.executor.executor import TestExecutor
from src.reporter.reporter import TestReporter
from src.scanner.scanner import TestScanner

console = Console()
logger = setup_logger()


def print_header():
    """Print application header"""
    console.print("\n[bold cyan]Test Radar[/bold cyan]")
    console.print("Intelligent Test Analysis System\n")


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to config file"
)
@click.pass_context
def cli(ctx, config: Optional[str]):
    """Test Radar - Intelligent Test Analysis System"""
    try:
        ctx.ensure_object(dict)
        # Use test_config.json by default if no config file is specified
        default_config = Path(__file__).parent / "test_config.json"
        ctx.obj["config"] = load_config(config if config else default_config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--pattern", "-p", default="test_*.py", help="Test file pattern")
@click.pass_context
def scan(ctx, paths: List[str], pattern: str):
    """Scan for tests in specified paths"""
    print_header()
    config = ctx.obj["config"]
    scanner = TestScanner(config.test)

    try:
        total_tests = 0
        for path in paths:
            path = Path(path)
            if path.is_file():
                tests = scanner.scan_file(path)
            else:
                tests = list(scanner.scan_directory(path, pattern))

            if not tests:
                logger.warning(f"No tests found in {path}")
                continue

            total_tests += len(tests)
            console.print(f"\nFound {len(tests)} tests in {path}:")
            for test in tests:
                console.print(f"  • {test.id}")

        console.print(f"\nTotal tests found: {total_tests}")

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--parallel/--no-parallel", default=True, help="Run tests in parallel")
@click.option("--coverage/--no-coverage", default=True, help="Collect coverage data")
@click.option("--report", "-r", type=click.Path(), help="Save report to file")
@click.pass_context
async def run(
    ctx, paths: List[str], parallel: bool, coverage: bool, report: Optional[str]
):
    """Run tests and analyze results"""
    print_header()
    config = ctx.obj["config"]

    # Initialize components
    scanner = TestScanner(config.test)
    executor = TestExecutor(config.test)
    reporter = TestReporter(config.test)
    analyzer = LLMAnalyzer(config.llm)

    try:
        # Scan for tests
        all_tests = []
        for path in paths:
            path = Path(path)
            if path.is_file():
                tests = scanner.scan_file(path)
            else:
                tests = list(scanner.scan_directory(path))
            all_tests.extend(tests)

        if not all_tests:
            logger.error("No tests found")
            sys.exit(1)

        console.print(f"\nRunning {len(all_tests)} tests...")

        # Run tests
        if not parallel:
            config.test.parallel_jobs = 1
        results = await executor.run_tests(all_tests)

        # Generate report
        test_report = reporter.generate_report(all_tests, results)
        reporter.print_report(test_report)

        if report:
            reporter.save_report(test_report, Path(report))
            console.print(f"\nReport saved to {report}")

        # Analyze results
        console.print("\nAnalyzing test results...")
        analyses = await analyzer.analyze_results(all_tests, results)

        # Print analysis summary
        console.print("\nAnalysis Summary:")
        for test_id, analysis in analyses.items():
            console.print(f"\n[cyan]Test: {test_id}[/cyan]")

            if analysis.issues:
                console.print("\n[red]Issues:[/red]")
                for issue in analysis.issues:
                    console.print(f"  • {issue}")

            if analysis.suggestions:
                console.print("\n[green]Suggestions:[/green]")
                for suggestion in analysis.suggestions:
                    console.print(f"  • {suggestion}")

            if analysis.coverage_gaps:
                console.print("\n[yellow]Coverage Gaps:[/yellow]")
                for gap in analysis.coverage_gaps:
                    console.print(f"  • {gap}")

        # Exit with status code based on results
        if test_report.failed_tests > 0 or test_report.error_tests > 0:
            sys.exit(1)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--fix/--no-fix", default=False, help="Automatically apply suggested fixes"
)
@click.pass_context
async def analyze(ctx, paths: List[str], fix: bool):
    """Analyze tests without running them"""
    print_header()
    config = ctx.obj["config"]
    scanner = TestScanner(config.test)
    analyzer = LLMAnalyzer(config.llm)

    try:
        # Scan for tests
        all_tests = []
        for path in paths:
            path = Path(path)
            if path.is_file():
                tests = scanner.scan_file(path)
            else:
                tests = list(scanner.scan_directory(path))
            all_tests.extend(tests)

        if not all_tests:
            logger.error("No tests found")
            sys.exit(1)

        console.print(f"\nAnalyzing {len(all_tests)} tests...")

        # Create dummy results for analysis
        results = {
            test.id: {"test_id": test.id, "status": "unknown", "duration": 0.0}
            for test in all_tests
        }

        # Analyze tests
        analyses = await analyzer.analyze_results(all_tests, results)

        # Print analysis
        for test_id, analysis in analyses.items():
            console.print(f"\n[cyan]Test: {test_id}[/cyan]")

            if analysis.issues:
                console.print("\n[red]Issues:[/red]")
                for issue in analysis.issues:
                    console.print(f"  • {issue}")

            if analysis.suggestions:
                console.print("\n[green]Suggestions:[/green]")
                for suggestion in analysis.suggestions:
                    console.print(f"  • {suggestion}")

            if fix and analysis.fixes:
                console.print("\n[yellow]Applying fixes...[/yellow]")
                for fix in analysis.fixes:
                    console.print(f"  • Would apply fix to {fix.file_path}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    try:
        cli(obj={})
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
