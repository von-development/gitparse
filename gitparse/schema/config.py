"""Configuration schemas for GitParse."""

from __future__ import annotations

from typing import Optional, list

from pydantic import BaseModel, Field


class ExtractionConfig(BaseModel):
    """Configuration for repository extraction behavior.

    Attributes:
        max_file_size (int): Maximum file size in bytes to process (default: 10MB)
        exclude_patterns (list[str]): Glob patterns for files to exclude
        include_patterns (list[str]): Glob patterns for files to include
        output_style (str): Style of output ("flattened", "markdown", "structured")
        temp_dir (Optional[str]): Directory for temporary files (e.g., cloned repos)
    """

    max_file_size: int = Field(default=10 * 1024 * 1024, description="Maximum file size in bytes")
    exclude_patterns: list[str] = Field(
        default_factory=list,
        description="Glob patterns to exclude",
    )
    include_patterns: list[str] = Field(
        default_factory=list,
        description="Glob patterns to include",
    )
    output_style: str = Field(default="flattened", description="Output format style")
    temp_dir: Optional[str] = Field(default=None, description="Directory for temporary files")
