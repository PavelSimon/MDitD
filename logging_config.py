"""
Centralized logging configuration for the MDitD application.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from settings import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    log_date_format: Optional[str] = None
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_format: Log message format string
        log_date_format: Log timestamp format string

    Raises:
        ValueError: If log level is invalid
        OSError: If log file cannot be created or accessed
    """
    # Use settings defaults if not provided
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    log_format = log_format or settings.log_format
    log_date_format = log_date_format or settings.log_date_format

    # Validate log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Create formatter
    formatter = logging.Formatter(
        fmt=log_format,
        datefmt=log_date_format
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Create rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            logging.info(f"Logging to file: {log_file}")

        except (OSError, IOError) as e:
            logging.error(f"Failed to set up file logging: {e}")
            # Continue with console logging only

    # Set specific logger levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("markitdown").setLevel(logging.WARNING)

    logging.info(f"Logging configured: level={log_level}, file={log_file or 'console only'}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_system_info() -> None:
    """Log system and application information for debugging."""
    import platform
    import os
    from pathlib import Path

    logger = get_logger(__name__)

    logger.info("=== MDitD Application Starting ===")
    logger.info(f"Application version: {settings.app_version}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Working directory: {Path.cwd()}")
    logger.info(f"Host: {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Max file size: {settings.get_max_file_size_mb()}MB")
    logger.info(f"Max concurrent files: {settings.max_concurrent_files}")
    logger.info("====================================")


def log_request_info(method: str, url: str, client_ip: str) -> None:
    """
    Log HTTP request information.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        client_ip: Client IP address
    """
    logger = get_logger("mditd.requests")
    logger.info(f"{method} {url} from {client_ip}")


def log_file_processing(filename: str, operation: str, success: bool, error: Optional[str] = None) -> None:
    """
    Log file processing operations.

    Args:
        filename: Name of the processed file
        operation: Operation performed (upload, convert, cleanup)
        success: Whether the operation was successful
        error: Error message if operation failed
    """
    logger = get_logger("mditd.files")

    if success:
        logger.info(f"File {operation}: {filename} - SUCCESS")
    else:
        logger.error(f"File {operation}: {filename} - FAILED - {error}")


def log_performance_metrics(operation: str, duration: float, file_count: int = 1) -> None:
    """
    Log performance metrics for operations.

    Args:
        operation: Operation name
        duration: Duration in seconds
        file_count: Number of files processed
    """
    logger = get_logger("mditd.performance")
    avg_time = duration / file_count if file_count > 0 else duration

    logger.info(
        f"Performance: {operation} - "
        f"Total: {duration:.2f}s, "
        f"Files: {file_count}, "
        f"Avg: {avg_time:.2f}s/file"
    )