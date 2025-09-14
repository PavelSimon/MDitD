"""
Configuration constants for MDitD application.
"""
from pathlib import Path

# File handling constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB
UPLOAD_CHUNK_SIZE = 8192
DEFAULT_UPLOADS_DIR = "uploads"
DEFAULT_OUTPUT_DIR = "vystup"

# Server constants
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8001
DEFAULT_RELOAD = True

# File validation constants
MAX_FILES_COUNT = 20  # Maximum number of files in single upload
MIN_FILE_SIZE = 1  # Minimum file size (1 byte)
MAX_FILENAME_LENGTH = 255
MAX_OUTPUT_DIR_LENGTH = 100

# File extension constants
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', 
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
    '.mp3', '.wav', '.m4a', '.flac',
    '.html', '.htm', '.csv', '.json', '.xml',
    '.zip', '.txt', '.md'
}

# Security constants
FORBIDDEN_FILENAME_PATTERNS = [
    '..',       # Directory traversal
    '/',        # Unix path separator
    '\\',       # Windows path separator
    ':',        # Drive separator (Windows)
    '*',        # Wildcard
    '?',        # Wildcard
    '"',        # Quote
    '<',        # Redirect
    '>',        # Redirect
    '|',        # Pipe
]

FORBIDDEN_OUTPUT_DIR_PATTERNS = [
    '..',       # Directory traversal
    '/',        # Absolute path
    '\\',       # Windows absolute path
    ':',        # Drive separator
]