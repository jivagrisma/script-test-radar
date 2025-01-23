"""
LLM-powered test analyzer implementation using AWS Bedrock.

Provides intelligent analysis of test results and code using Claude through AWS Bedrock.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from botocore.config import Config
from pydantic import BaseModel

from ..core.config import LLMConfig
from ..core.exceptions import LLMError
from ..core.logger import get_logger
from ..executor.executor import TestResult
from ..scanner.scanner import TestInfo

logger = get_logger(__name__)


class CodeFix(BaseModel):
    """Represents a suggested code fix."""

    file_path: Path
    line_start: int
    line_end: int
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float


class TestAnalysis(BaseModel):
    """Analysis results for a test."""

    test_id: str
    issues: List[str]
    suggestions: List[str]
    fixes: List[CodeFix]
    coverage_gaps: List[str]


class BedrockLLM:
    """AWS Bedrock LLM client with enhanced features."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize Bedrock client with advanced configuration.

        Args:
            config: LLM configuration including AWS credentials and model settings.
        """
        self.config = config

        # Configure AWS client with retry logic
        aws_config = Config(
            region_name=config.aws.region,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        # Initialize Bedrock client with credentials
        self.client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=aws_config,
        )

    async def generate(self, prompt: str) -> str:
        """Generate response from Claude with enhanced error handling.

        Args:
            prompt: Input prompt.

        Returns:
            Generated response.

        Raises:
            LLMError: If generation fails with detailed error information.
        """
        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }

            # Invoke model
            response = self.client.invoke_model(
                modelId=self.config.aws.bedrock_model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"]

        except Exception as e:
            # Enhanced error handling with specific error types
            if "ValidationException" in str(e):
                if "inference profile" in str(e):
                    raise LLMError(
                        "AWS Bedrock requires an inference profile for this model. "
                        "Please configure an inference profile in the AWS Console.",
                        cause=e,
                    )
                raise LLMError(f"Invalid request to AWS Bedrock: {str(e)}", cause=e)
            if "AccessDeniedException" in str(e):
                raise LLMError(
                    "Access denied to AWS Bedrock. Please verify your AWS credentials and permissions.",
                    cause=e,
                )
            if "ResourceNotFoundException" in str(e):
                raise LLMError(
                    f"Model {self.config.aws.bedrock_model_id} not found in region {self.config.aws.region}",
                    cause=e,
                )
            if "ThrottlingException" in str(e):
                raise LLMError(
                    "Request throttled by AWS Bedrock. Please reduce request rate or increase quota.",
                    cause=e,
                )
            raise LLMError(f"Failed to generate response: {str(e)}", cause=e)


class LocalAnalyzer:
    """Fallback analyzer that provides basic analysis without LLM."""

    def analyze_test(self, test: TestInfo, result: TestResult) -> TestAnalysis:
        """Analyze a test using basic heuristics.

        Args:
            test: Test to analyze.
            result: Test execution result.

        Returns:
            Basic test analysis.
        """
        issues: List[str] = []
        suggestions: List[str] = []

        # Enhanced local analysis
        if result.status == "error":
            issues.append("Test failed with an error")
            suggestions.append("Review test setup and dependencies")

        if result.duration > 2.0:
            issues.append("Test execution time is high")
            suggestions.append("Consider optimizing test performance")

        if not result.coverage:
            issues.append("No coverage information available")
            suggestions.append("Enable coverage reporting")

        # Check for common patterns
        if result.stdout and "warning" in result.stdout.lower():
            issues.append("Test generated warnings")
            suggestions.append("Address test warnings")

        if result.stderr and "deprecation" in result.stderr.lower():
            issues.append("Test uses deprecated features")
            suggestions.append("Update deprecated functionality")

        return TestAnalysis(
            test_id=test.id,
            issues=issues,
            suggestions=suggestions,
            fixes=[],
            coverage_gaps=["Coverage analysis not available"],
        )


class LLMAnalyzer:
    """Analyzer that uses Claude through AWS Bedrock for intelligent test analysis."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize analyzer with configuration.

        Args:
            config: Configuration for LLM and analysis.
        """
        self.config = config
        self.llm = BedrockLLM(config)
        self.local = LocalAnalyzer()

    def _create_analysis_prompt(
        self, test: TestInfo, result: TestResult, code_context: str
    ) -> str:
        """Create enhanced prompt for test analysis.

        Args:
            test: Test information.
            result: Test execution result.
            code_context: Related code context.

        Returns:
            Formatted prompt for Claude.
        """
        prompt = f"""
        Please analyze this Python test and its execution result:

        Test Information:
        - ID: {test.id}
        - File: {test.file_path}
        - Line: {test.line_number}
        - Class: {test.class_name or 'None'}

        Test Result:
        - Status: {result.status}
        - Duration: {result.duration:.2f}s
        - Coverage: {result.coverage or 'N/A'}%

        Code Context:
        ```python
        {code_context}
        ```

        Execution Output:
        ```
        {result.stdout or ''}
        ```

        Error Output:
        ```
        {result.stderr or ''}
        ```

        Please provide:
        1. List of potential issues in the test
        2. Suggestions for improvement
        3. Specific code fixes if applicable
        4. Coverage gaps and areas needing more testing

        Focus on:
        - Test reliability and robustness
        - Code quality and best practices
        - Coverage optimization
        - Performance improvements

        Format your response in sections:

        Issues:
        - Issue 1
        - Issue 2

        Suggestions:
        - Suggestion 1
        - Suggestion 2

        Code Fixes:
        ```python
        # Original code
        [original code block]
        ```
        ```python
        # Suggested fix
        [fixed code block]
        ```

        Coverage Gaps:
        - Gap 1
        - Gap 2
        """
        return prompt

    def _parse_claude_response(self, response: str) -> TestAnalysis:
        """Parse Claude's response into structured analysis with enhanced error handling.

        Args:
            response: Raw response from Claude.

        Returns:
            Structured test analysis.

        Raises:
            LLMError: If response cannot be parsed.
        """
        try:
            # Extract sections from response
            sections = response.split("\n\n")

            issues: List[str] = []
            suggestions: List[str] = []
            fixes: List[CodeFix] = []
            coverage_gaps: List[str] = []

            current_section: Optional[str] = None

            for section in sections:
                if section.startswith("Issues:"):
                    current_section = "issues"
                    continue
                elif section.startswith("Suggestions:"):
                    current_section = "suggestions"
                    continue
                elif section.startswith("Code Fixes:"):
                    current_section = "fixes"
                    continue
                elif section.startswith("Coverage Gaps:"):
                    current_section = "coverage"
                    continue

                if current_section == "issues":
                    issues.extend(
                        line.strip("- ") for line in section.split("\n") if line.strip()
                    )
                elif current_section == "suggestions":
                    suggestions.extend(
                        line.strip("- ") for line in section.split("\n") if line.strip()
                    )
                elif current_section == "fixes":
                    # Enhanced code fix parsing
                    if "```" in section:
                        blocks = section.split("```")
                        for i in range(1, len(blocks) - 1, 2):
                            original = blocks[i].strip()
                            suggested = blocks[i + 1].strip()
                            if "python" in original:
                                original = "\n".join(original.split("\n")[1:])
                            if "python" in suggested:
                                suggested = "\n".join(suggested.split("\n")[1:])

                            fixes.append(
                                CodeFix(
                                    file_path=Path("dummy.py"),
                                    line_start=0,
                                    line_end=0,
                                    original_code=original.strip(),
                                    suggested_code=suggested.strip(),
                                    explanation="",
                                    confidence=0.8,
                                )
                            )
                elif current_section == "coverage":
                    coverage_gaps.extend(
                        line.strip("- ") for line in section.split("\n") if line.strip()
                    )

            return TestAnalysis(
                test_id="dummy",
                issues=issues,
                suggestions=suggestions,
                fixes=fixes,
                coverage_gaps=coverage_gaps,
            )

        except Exception as e:
            raise LLMError("Failed to parse Claude response", cause=e)

    async def analyze_test(
        self, test: TestInfo, result: TestResult, code_context: str
    ) -> TestAnalysis:
        """Analyze a test using Claude with enhanced error handling.

        Args:
            test: Test to analyze.
            result: Test execution result.
            code_context: Related code context.

        Returns:
            Test analysis results.

        Raises:
            LLMError: If analysis fails.
        """
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(test, result, code_context)

            try:
                # Try LLM analysis first
                response = await self.llm.generate(prompt)
                analysis = self._parse_claude_response(response)
                analysis.test_id = test.id

                # Update fix metadata
                for fix in analysis.fixes:
                    fix.file_path = test.file_path

                return analysis

            except LLMError as e:
                # Fall back to local analysis if LLM fails
                logger.warning(
                    f"LLM analysis failed, falling back to local analysis: {e}"
                )
                return self.local.analyze_test(test, result)

        except Exception as e:
            raise LLMError(f"Failed to analyze test {test.id}", cause=e)

    async def analyze_results(
        self, tests: List[TestInfo], results: Dict[str, TestResult]
    ) -> Dict[str, TestAnalysis]:
        """Analyze multiple test results with enhanced error handling.

        Args:
            tests: List of tests.
            results: Test execution results.

        Returns:
            Dictionary mapping test IDs to analysis results.
        """
        analyses: Dict[str, TestAnalysis] = {}

        for test in tests:
            result = results.get(test.id)
            if not result:
                continue

            # Get code context by reading test file
            try:
                with open(test.file_path, "r", encoding="utf-8") as f:
                    code_context = f.read()
            except Exception as e:
                logger.warning(f"Failed to read test file {test.file_path}: {e}")
                code_context = "# Failed to read test file"

            try:
                analysis = await self.analyze_test(test, result, code_context)
                analyses[test.id] = analysis
            except Exception as e:
                logger.error(f"Failed to analyze test {test.id}: {e}")
                # Continue with next test on error
                continue

        return analyses
