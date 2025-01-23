"""
Configuration management for test-radar.

Handles loading and validation of configuration from files and environment variables.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TestConfig(BaseModel):
    """Test execution configuration."""

    python_path: str = "python3"
    test_paths: List[str] = []
    exclude_patterns: List[str] = ["__pycache__", ".pytest_cache"]
    parallel_jobs: int = 0
    timeout: int = 300
    coverage_target: float = 95.0


class VSCodeConfig(BaseModel):
    """VSCode integration configuration."""

    auto_discover: bool = True
    show_output: bool = True
    debug_config: Dict[str, Any] = {}


class AWSConfig(BaseModel):
    """AWS Bedrock configuration."""

    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"anthropic-beta": "prompt-caching-2024-07-31"}
    )


class LLMConfig(BaseModel):
    """LLM configuration."""

    temperature: float = 0.0
    max_tokens: int = 8192
    context_window: int = 100000
    aws: AWSConfig


class RadarConfig(BaseModel):
    """Main configuration."""

    test: TestConfig
    vscode: VSCodeConfig
    llm: LLMConfig
    log_level: str = "INFO"
    cache_dir: str = ".cache"
    report_dir: str = "reports"
    report_format: str = "html"


def load_config(config_path: Optional[Union[str, Path]] = None) -> RadarConfig:
    """Load configuration from file and environment variables.

    Args:
        config_path: Optional path to config file.

    Returns:
        Loaded configuration.

    Raises:
        FileNotFoundError: If config file not found.
        ValueError: If config is invalid.
    """
    # Default config path
    if not config_path:
        config_path = os.getenv("TEST_RADAR_CONFIG", "test_config.json")

    if isinstance(config_path, str):
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load config file
    with open(config_path) as f:
        config_data = json.load(f)

    # Override with environment variables
    config_data["test"]["python_path"] = os.getenv(
        "PYTHON_PATH", config_data["test"]["python_path"]
    )
    config_data["test"]["parallel_jobs"] = int(
        os.getenv("TEST_PARALLEL_JOBS", str(config_data["test"]["parallel_jobs"]))
    )
    config_data["test"]["timeout"] = int(
        os.getenv("TEST_TIMEOUT", str(config_data["test"]["timeout"]))
    )
    config_data["test"]["coverage_target"] = float(
        os.getenv("TEST_COVERAGE_TARGET", str(config_data["test"]["coverage_target"]))
    )

    config_data["vscode"]["auto_discover"] = (
        os.getenv("VSCODE_AUTO_DISCOVER", "true").lower() == "true"
    )
    config_data["vscode"]["show_output"] = (
        os.getenv("VSCODE_SHOW_OUTPUT", "true").lower() == "true"
    )

    # AWS Bedrock configuration
    config_data["llm"]["aws"]["access_key_id"] = os.getenv(
        "AWS_ACCESS_KEY_ID", config_data["llm"]["aws"]["access_key_id"]
    )
    config_data["llm"]["aws"]["secret_access_key"] = os.getenv(
        "AWS_SECRET_ACCESS_KEY", config_data["llm"]["aws"]["secret_access_key"]
    )
    config_data["llm"]["aws"]["region"] = os.getenv(
        "AWS_REGION", config_data["llm"]["aws"]["region"]
    )
    config_data["llm"]["aws"]["bedrock_model_id"] = os.getenv(
        "AWS_BEDROCK_MODEL_ID", config_data["llm"]["aws"]["bedrock_model_id"]
    )

    # Parse headers from environment if provided
    headers_env = os.getenv("AWS_BEDROCK_HEADERS")
    if headers_env:
        try:
            config_data["llm"]["aws"]["headers"] = json.loads(headers_env)
        except json.JSONDecodeError:
            raise ValueError("Invalid AWS_BEDROCK_HEADERS format. Must be valid JSON.")

    # LLM configuration
    config_data["llm"]["temperature"] = float(
        os.getenv("LLM_TEMPERATURE", str(config_data["llm"]["temperature"]))
    )
    config_data["llm"]["max_tokens"] = int(
        os.getenv("LLM_MAX_TOKENS", str(config_data["llm"]["max_tokens"]))
    )
    config_data["llm"]["context_window"] = int(
        os.getenv("LLM_CONTEXT_WINDOW", str(config_data["llm"]["context_window"]))
    )

    config_data["log_level"] = os.getenv("LOG_LEVEL", config_data["log_level"])
    config_data["cache_dir"] = os.getenv("CACHE_DIR", config_data["cache_dir"])
    config_data["report_dir"] = os.getenv("REPORT_DIR", config_data["report_dir"])
    config_data["report_format"] = os.getenv(
        "REPORT_FORMAT", config_data["report_format"]
    )

    # Validate and create config object
    try:
        return RadarConfig(**config_data)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {str(e)}")


def get_default_config() -> RadarConfig:
    """Get default configuration.

    Returns:
        Default configuration.
    """
    return RadarConfig(
        test=TestConfig(),
        vscode=VSCodeConfig(),
        llm=LLMConfig(aws=AWSConfig(access_key_id="", secret_access_key="")),
    )
