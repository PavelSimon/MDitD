"""
Configuration constants for MDitD application.
DEPRECATED: This module is being replaced by settings.py with pydantic-settings.
Kept for backward compatibility during migration.
"""
import warnings
from settings import settings

# Deprecation warning
warnings.warn(
    "config.py is deprecated. Use settings.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# File handling constants (mapped from settings)
MAX_FILE_SIZE = settings.max_file_size
MAX_TOTAL_SIZE = settings.max_total_size
UPLOAD_CHUNK_SIZE = settings.upload_chunk_size
DEFAULT_UPLOADS_DIR = settings.uploads_dir
DEFAULT_OUTPUT_DIR = settings.output_dir

# Server constants (mapped from settings)
DEFAULT_HOST = settings.host
DEFAULT_PORT = settings.port
DEFAULT_RELOAD = settings.reload

# File validation constants (mapped from settings)
MAX_FILES_COUNT = settings.max_files_count
MIN_FILE_SIZE = settings.min_file_size
MAX_FILENAME_LENGTH = settings.max_filename_length
MAX_OUTPUT_DIR_LENGTH = settings.max_output_dir_length

# File extension constants (mapped from settings)
SUPPORTED_EXTENSIONS = settings.supported_extensions

# Security constants (mapped from settings)
FORBIDDEN_FILENAME_PATTERNS = settings.forbidden_filename_patterns
FORBIDDEN_OUTPUT_DIR_PATTERNS = settings.forbidden_output_dir_patterns