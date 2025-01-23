"""
Test scanner implementation.

Provides functionality to discover and analyze test files.
"""

import ast
import re
from pathlib import Path
from typing import Generator, List, Optional, Set

from ..core.config import TestConfig
from ..core.exceptions import ScanError
from ..core.logger import get_logger

logger = get_logger(__name__)


class TestInfo:
    """Information about a discovered test."""

    def __init__(
        self,
        id: str,
        file_path: Path,
        line_number: int,
        class_name: Optional[str] = None,
        function_name: str = "",
        description: str = "",
        markers: Optional[List[str]] = None,
    ) -> None:
        """Initialize test information.

        Args:
            id: Unique test identifier.
            file_path: Path to test file.
            line_number: Line number where test is defined.
            class_name: Optional containing class name.
            function_name: Test function name.
            description: Test description from docstring.
            markers: Optional list of test markers.
        """
        self.id = id
        self.file_path = file_path
        self.line_number = line_number
        self.class_name = class_name
        self.function_name = function_name
        self.description = description
        self.markers = markers or []


class TestVisitor(ast.NodeVisitor):
    """AST visitor to find test functions and classes."""

    def __init__(self, file_path: Path) -> None:
        """Initialize test visitor.

        Args:
            file_path: Path to file being visited.
        """
        self.file_path = file_path
        self.tests: List[TestInfo] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition.

        Args:
            node: Class definition node.
        """
        # Check if it's a test class
        is_test_class = False
        for base in node.bases:
            if ((isinstance(base, ast.Name) and base.id == "TestCase") or
                (isinstance(base, ast.Attribute) and base.attr == "TestCase")):
                is_test_class = True
                break

        if is_test_class or node.name.startswith("Test"):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition.

        Args:
            node: Function definition node.
        """
        # Check if it's a test function
        if node.name.startswith("test_") or any(
            isinstance(dec, ast.Name) and dec.id == "pytest"
            for dec in node.decorator_list
        ):
            # Extract description from docstring
            description = ast.get_docstring(node) or ""

            # Extract markers from decorators
            markers: List[str] = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.attr in ["mark", "marker"] and dec.args:
                        if isinstance(dec.args[0], ast.Constant):
                            markers.append(str(dec.args[0].value))

            # Create unique test ID
            test_id = f"{self.file_path.stem}::{self.current_class or ''}"
            if self.current_class:
                test_id += f"::{node.name}"
            else:
                test_id += f"::{node.name}"

            self.tests.append(
                TestInfo(
                    id=test_id,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=self.current_class,
                    function_name=node.name,
                    description=description,
                    markers=markers,
                )
            )


class TestScanner:
    """Scanner for discovering tests in Python files."""

    def __init__(self, config: TestConfig) -> None:
        """Initialize scanner with configuration.

        Args:
            config: Test configuration.
        """
        self.config = config

    def scan_file(self, file_path: Path) -> List[TestInfo]:
        """Scan a single file for tests.

        Args:
            file_path: Path to file to scan.

        Returns:
            List of discovered tests.

        Raises:
            ScanError: If file cannot be scanned.
        """
        try:
            # Read and parse file
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            # Find tests
            visitor = TestVisitor(file_path)
            visitor.visit(tree)

            return visitor.tests

        except Exception as e:
            raise ScanError(f"Failed to scan file {file_path}: {str(e)}")

    def scan_directory(
        self, directory: Path, pattern: str = "test_*.py"
    ) -> Generator[TestInfo, None, None]:
        """Scan a directory recursively for test files.

        Args:
            directory: Directory to scan.
            pattern: Glob pattern for test files.

        Yields:
            Discovered tests.

        Raises:
            ScanError: If directory cannot be scanned.
        """
        try:
            # Compile exclude patterns
            exclude_patterns = [
                re.compile(pattern) for pattern in self.config.exclude_patterns
            ]

            # Walk directory
            for path in directory.rglob(pattern):
                # Check if path should be excluded
                if any(p.match(str(path)) for p in exclude_patterns):
                    continue

                try:
                    yield from self.scan_file(path)
                except Exception as e:
                    logger.warning(f"Failed to scan {path}: {e}")
                    continue

        except Exception as e:
            raise ScanError(f"Failed to scan directory {directory}: {str(e)}")

    def get_test_dependencies(self, test: TestInfo) -> List[Path]:
        """Get dependencies for a test.

        Args:
            test: Test to get dependencies for.

        Returns:
            List of dependency file paths.
        """
        try:
            deps: Set[Path] = set()

            # Add test file
            deps.add(test.file_path)

            # Parse imports
            with open(test.file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            # Find all imports
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = node.module if isinstance(node, ast.ImportFrom) else None
                    if module:
                        # Convert module to path
                        parts = module.split(".")
                        path = Path(*parts).with_suffix(".py")
                        if path.exists():
                            deps.add(path)

            return list(deps)

        except Exception as e:
            logger.warning(f"Failed to get dependencies for {test.id}: {e}")
            return [test.file_path]
