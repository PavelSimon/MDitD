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

# File extension constants
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', 
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
    '.mp3', '.wav', '.m4a', '.flac',
    '.html', '.htm', '.csv', '.json', '.xml',
    '.zip', '.txt', '.md'
}