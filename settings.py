"""
Application settings and configuration management.
"""
from pathlib import Path
from typing import Optional, Set
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden using environment variables with MDITD_ prefix.
    For example: MDITD_HOST=localhost, MDITD_PORT=8080, etc.
    """

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8001, description="Server port number")
    reload: bool = Field(default=True, description="Enable auto-reload for development")

    # File size limits
    max_file_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Maximum file size in bytes"
    )
    max_total_size: int = Field(
        default=500 * 1024 * 1024,  # 500MB
        description="Maximum total upload size in bytes"
    )
    max_files_count: int = Field(
        default=20,
        description="Maximum number of files per upload"
    )
    min_file_size: int = Field(
        default=1,
        description="Minimum file size in bytes"
    )

    # Directory configuration
    uploads_dir: str = Field(default="uploads", description="Temporary uploads directory")
    output_dir: str = Field(default="vystup", description="Default output directory")
    static_dir: str = Field(default="static", description="Static files directory")
    templates_dir: str = Field(default="templates", description="Templates directory")

    # File processing
    upload_chunk_size: int = Field(
        default=8192,
        description="Chunk size for streaming uploads in bytes"
    )
    max_concurrent_files: int = Field(
        default=4,
        description="Maximum number of files processed concurrently"
    )

    # Filename constraints
    max_filename_length: int = Field(
        default=255,
        description="Maximum filename length in characters"
    )
    max_output_dir_length: int = Field(
        default=100,
        description="Maximum output directory name length"
    )

    # Security settings
    forbidden_filename_patterns: list[str] = Field(
        default_factory=lambda: ['<', '>', ':', '"', '|', '?', '*', '\x00', '\n', '\r'],
        description="Forbidden characters in filenames"
    )
    forbidden_output_dir_patterns: list[str] = Field(
        default_factory=lambda: ['..', '\\', '/', ':', '*', '?', '"', '<', '>', '|'],
        description="Forbidden patterns in output directory names"
    )

    # Supported file extensions
    supported_extensions: set[str] = Field(
        default_factory=lambda: {
            '.pdf', '.docx', '.pptx', '.xlsx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.mp3', '.wav', '.m4a', '.flac',
            '.html', '.htm', '.csv', '.json', '.xml',
            '.zip', '.txt', '.md'
        },
        description="Set of supported file extensions"
    )

    # Application metadata
    app_title: str = Field(default="MDitD - MarkItDown Web App", description="Application title")
    app_description: str = Field(
        default="Convert documents to Markdown via web interface",
        description="Application description"
    )
    app_version: str = Field(default="0.2.0", description="Application version")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Optional log file path")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    log_date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Log timestamp format"
    )

    # Development settings
    debug: bool = Field(default=False, description="Enable debug mode")

    model_config = SettingsConfigDict(
        env_prefix="MDITD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def get_uploads_path(self) -> Path:
        """Get uploads directory as Path object."""
        return Path(self.uploads_dir)

    def get_output_path(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.output_dir)

    def get_static_path(self) -> Path:
        """Get static files directory as Path object."""
        return Path(self.static_dir)

    def get_templates_path(self) -> Path:
        """Get templates directory as Path object."""
        return Path(self.templates_dir)

    def is_extension_supported(self, extension: str) -> bool:
        """Check if file extension is supported."""
        return extension.lower() in self.supported_extensions

    def get_max_file_size_mb(self) -> int:
        """Get maximum file size in MB."""
        return self.max_file_size // (1024 * 1024)

    def get_max_total_size_mb(self) -> int:
        """Get maximum total size in MB."""
        return self.max_total_size // (1024 * 1024)


# Global settings instance
settings = Settings()