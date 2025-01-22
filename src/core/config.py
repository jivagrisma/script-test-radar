"""
Configuration management for test-radar.
Handles all configuration settings and provides validation through Pydantic models.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

class TestConfig(BaseModel):
    """Base configuration for test execution"""
    python_path: str = Field(default="python3.11", description="Python interpreter to use")
    test_paths: List[Path] = Field(default_factory=list, description="Paths to test files/directories")
    exclude_patterns: List[str] = Field(default_factory=lambda: [".*", "__pycache__"], 
                                      description="Patterns to exclude")
    parallel_jobs: int = Field(default=0, description="Number of parallel jobs (0 = auto)")
    timeout: int = Field(default=300, description="Test timeout in seconds")
    coverage_target: float = Field(default=95.0, description="Target coverage percentage")
    
    @validator('parallel_jobs')
    def validate_jobs(cls, v: int) -> int:
        """Validate number of parallel jobs"""
        if v < 0:
            raise ValueError("parallel_jobs must be >= 0")
        return v

class VSCodeConfig(BaseModel):
    """VSCode integration configuration"""
    auto_discover: bool = Field(default=True, description="Auto-discover tests on file changes")
    show_output: bool = Field(default=True, description="Show test output in VSCode")
    debug_config: Dict[str, Any] = Field(default_factory=dict, description="Debug configuration")
    decoration_enabled: bool = Field(default=True, description="Enable error decorations")

class AWSConfig(BaseModel):
    """AWS configuration"""
    access_key_id: str = Field(..., description="AWS access key ID")
    secret_access_key: str = Field(..., description="AWS secret access key")
    region: str = Field(default="us-east-1", description="AWS region")
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0",
        description="AWS Bedrock model ID"
    )
    
    @validator('region')
    def validate_region(cls, v: str) -> str:
        """Validate AWS region"""
        valid_regions = [
            "us-east-1", "us-west-2", "eu-west-1",
            "ap-southeast-1", "ap-northeast-1"
        ]
        if v not in valid_regions:
            raise ValueError(f"region must be one of {valid_regions}")
        return v

class LLMConfig(BaseModel):
    """Configuration for LLM integration"""
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=2000, description="Maximum tokens per request")
    context_window: int = Field(default=100000, description="Context window size")
    aws: AWSConfig = Field(..., description="AWS configuration")
    
    @validator('temperature')
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature range"""
        if not 0 <= v <= 1:
            raise ValueError("temperature must be between 0 and 1")
        return v

class RadarConfig(BaseModel):
    """Main configuration class"""
    test: TestConfig = Field(default_factory=TestConfig, description="Test configuration")
    vscode: VSCodeConfig = Field(default_factory=VSCodeConfig, description="VSCode configuration")
    llm: LLMConfig = Field(..., description="LLM configuration")
    log_level: str = Field(default="INFO", description="Logging level")
    cache_dir: Path = Field(default=Path(".cache"), description="Cache directory")
    report_dir: Path = Field(default=Path("reports"), description="Report directory")
    report_format: str = Field(default="html", description="Report format")
    
    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v
    
    @validator('report_format')
    def validate_report_format(cls, v: str) -> str:
        """Validate report format"""
        valid_formats = ["html", "json", "txt"]
        v = v.lower()
        if v not in valid_formats:
            raise ValueError(f"report_format must be one of {valid_formats}")
        return v

    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True

def load_config(config_path: Union[str, Path]) -> RadarConfig:
    """Load configuration from file"""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        config_dict = config_path.read_text()
        return RadarConfig.model_validate_json(config_dict)
    except Exception as e:
        raise ValueError(f"Failed to load config: {e}") from e

def save_config(config: RadarConfig, config_path: Union[str, Path]) -> None:
    """Save configuration to file"""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        config_path.write_text(config.model_dump_json(indent=2))
    except Exception as e:
        raise ValueError(f"Failed to save config: {e}") from e