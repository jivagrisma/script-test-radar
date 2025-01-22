"""
Test scanner implementation.
Provides functionality for discovering and analyzing test files.
"""

import ast
from pathlib import Path
from typing import Dict, Generator, List, Optional, Set, Tuple

from ..core.config import TestConfig
from ..core.exceptions import ScannerError
from ..core.logger import get_logger

logger = get_logger(__name__)

class TestInfo:
    """Information about a discovered test"""
    
    def __init__(
        self,
        name: str,
        file_path: Path,
        line_number: int,
        class_name: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.name = name
        self.file_path = file_path
        self.line_number = line_number
        self.class_name = class_name
        self.description = description
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique test identifier"""
        if self.class_name:
            return f"{self.file_path}::{self.class_name}::{self.name}"
        return f"{self.file_path}::{self.name}"
    
    def __repr__(self) -> str:
        return f"<TestInfo {self.id}>"

class TestVisitor(ast.NodeVisitor):
    """AST visitor for discovering tests"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.current_class: Optional[str] = None
        self.tests: List[TestInfo] = []
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition"""
        # Check if it's a test class
        if any(base.id == 'TestCase' for base in node.bases if isinstance(base, ast.Name)):
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = None
        else:
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition"""
        # Check if it's a test function
        if node.name.startswith('test_'):
            description = ast.get_docstring(node)
            self.tests.append(
                TestInfo(
                    name=node.name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=self.current_class,
                    description=description
                )
            )

class TestScanner:
    """Scanner for discovering tests in Python files"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.cache: Dict[Path, List[TestInfo]] = {}
    
    def scan_file(self, file_path: Path) -> List[TestInfo]:
        """Scan a single file for tests
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of discovered tests
            
        Raises:
            ScannerError: If file cannot be parsed
        """
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            visitor = TestVisitor(file_path)
            visitor.visit(tree)
            
            self.cache[file_path] = visitor.tests
            return visitor.tests
            
        except Exception as e:
            raise ScannerError(f"Failed to scan {file_path}", cause=e)
    
    def scan_directory(
        self,
        directory: Path,
        pattern: str = "test_*.py"
    ) -> Generator[TestInfo, None, None]:
        """Scan directory recursively for test files
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for test files
            
        Yields:
            Discovered tests
        """
        try:
            for file_path in directory.rglob(pattern):
                if any(p in file_path.parts for p in self.config.exclude_patterns):
                    continue
                    
                yield from self.scan_file(file_path)
                
        except Exception as e:
            raise ScannerError(f"Failed to scan directory {directory}", cause=e)
    
    def scan(self) -> List[TestInfo]:
        """Scan all configured test paths
        
        Returns:
            List of all discovered tests
        """
        all_tests: List[TestInfo] = []
        
        for path in self.config.test_paths:
            path = Path(path)
            if path.is_file():
                all_tests.extend(self.scan_file(path))
            elif path.is_dir():
                all_tests.extend(self.scan_directory(path))
            else:
                logger.warning(f"Path does not exist: {path}")
        
        return all_tests
    
    def clear_cache(self) -> None:
        """Clear the scanner cache"""
        self.cache.clear()